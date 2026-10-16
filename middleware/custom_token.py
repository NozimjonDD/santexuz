from django.contrib.auth import get_user_model
from rest_framework import status, exceptions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from datetime import timedelta, datetime, timezone

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'user_role': user.role,
        })


class OLDCustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that distinguishes between:
      - Invalid/expired credentials → 401
      - Other input errors → 400
    """
    # def validate(self, attrs):
    #     try:
    #         data = super().validate(attrs)
    #     except TokenError as e:
    #         # Any token parsing/validation error
    #         raise exceptions.AuthenticationFailed(
    #             detail="Invalid or expired token.",
    #             code=status.HTTP_401_UNAUTHORIZED
    #         )
    #     except exceptions.AuthenticationFailed as e:
    #         # Wrong password, inactive account, etc.
    #         raise exceptions.AuthenticationFailed(
    #             detail=str(e.detail),
    #             code=status.HTTP_401_UNAUTHORIZED
    #         )
    #     except Exception as e:
    #         # Other unexpected validation problems → 400
    #         raise exceptions.ValidationError(
    #             detail=str(e),
    #             code=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Dynamically adjust token lifetime per user type.
    """

    def get_token(self, user):
        token = super().get_token(user)

        # Define token lifetimes based on user role
        if user.role == "admin":
            access_lifetime = timedelta(hours=1)
            refresh_lifetime = timedelta(days=2)
            role = "admin"
        elif user.role == "internal":
            access_lifetime = timedelta(days=365)
            refresh_lifetime = timedelta(days=730)
            role = "internal"
        else:
            access_lifetime = timedelta(days=1)
            refresh_lifetime = timedelta(days=7)
            role = "ordinary"

        # Set token expiration and add custom claims
        token.set_exp(lifetime=access_lifetime)
        token["role"] = role

        # Generate refresh token with custom expiration
        refresh_token = RefreshToken.for_user(user)
        refresh_token.set_exp(lifetime=refresh_lifetime)
        token["refresh_token"] = str(refresh_token)

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        token = self.get_token(self.user)
        refresh_token_str = token["refresh_token"]
        refresh_token = RefreshToken(refresh_token_str)

        # Add expiration times to the response
        data.update({
            "role": token["role"],
            "expire_in": datetime.fromtimestamp(token["exp"], tz=timezone.utc).isoformat(),
            "refresh_expire": datetime.fromtimestamp(refresh_token["exp"], tz=timezone.utc).isoformat(),
        })

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    # serializer_class = MyTokenObtainPairSerializer
    serializer_class = CustomTokenObtainPairSerializer


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Custom refresh serializer that:
    - Decodes the provided refresh token.
    - Issues a new access token with role-based lifetime.
    - Returns both expire timestamps and role.
    """

    def validate(self, attrs):
        try:
            # Decode the incoming refresh token
            refresh = RefreshToken(attrs["refresh"])

            # --- Retrieve user safely ---
            try:
                user_id = refresh["user_id"]
                user = User.objects.get(id=user_id)
            except Exception:
                raise InvalidToken("Invalid refresh token: user not found")

            # Rebuild lifetimes based on user role
            if user.role == "admin":
                access_lifetime = timedelta(hours=1)
                refresh_lifetime = timedelta(days=2)
                role = "admin"
            elif user.role == "internal":
                access_lifetime = timedelta(days=365)
                refresh_lifetime = timedelta(days=730)
                role = "internal"
            else:
                access_lifetime = timedelta(days=1)
                refresh_lifetime = timedelta(days=7)
                role = "ordinary"

            # Generate new access token
            access = AccessToken.for_user(user)
            access.set_exp(lifetime=access_lifetime)
            access["role"] = role

            # Generate new refresh token (rotation)
            new_refresh = RefreshToken.for_user(user)
            new_refresh.set_exp(lifetime=refresh_lifetime)
            new_refresh["role"] = role

            # Compute expirations
            access_expire = datetime.fromtimestamp(access["exp"], tz=timezone.utc)
            refresh_expire = datetime.fromtimestamp(new_refresh["exp"], tz=timezone.utc)

            # Return payload
            data = {
                "access": str(access),
                "expire_in": access_expire.isoformat(),
                "refresh": str(new_refresh),
                "refresh_expire": refresh_expire.isoformat(),
                "role": role,
            }

            return data

        except TokenError as e:
            raise InvalidToken(f"Token is invalid or expired: {e}")


class RefreshTokenSerializer(TokenRefreshSerializer):
    """
    Refreshes access token and returns refresh token's expiration timestamp.
    """

    def validate(self, attrs):
        # Step 1: Run base validation — generates new access token
        data = super().validate(attrs)

        try:
            # Step 2: Decode the refresh token from incoming request
            refresh_token = RefreshToken(attrs["refresh"])

            # Step 3: Extract its expiration timestamp
            expire_time = datetime.fromtimestamp(refresh_token["exp"], tz=timezone.utc)
            data["refresh_expire"] = expire_time.isoformat()

            access_token = data["access"]
            # data["access_expire"] = datetime.fromtimestamp(access_token["exp"], tz=timezone.utc).isoformat()
            data["role"] = refresh_token.get("role", None)

        except TokenError as e:
            raise InvalidToken(f"Invalid or expired refresh token: {e}")

        return data


class RefreshTokenView(TokenRefreshView):
    # serializer_class = RefreshTokenSerializer
    serializer_class = CustomTokenRefreshSerializer
