from django.db import transaction
from django.http import Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.audit import record
from apps.common.development import local_preview_enabled
from apps.users.models import User
from .serializers import ProfileSerializer


@method_decorator(csrf_protect, name="dispatch")
class LocalPreviewLoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(exclude=True)
    @transaction.atomic
    def post(self, request):
        if not local_preview_enabled(request):
            raise Http404
        data = LocalPreviewInput(data=request.data)
        data.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            username="__santex_local_preview__",
            defaults={"role": "customer", "first_name": "Dev", "last_name": "Preview",
                      "email": "local-preview@invalid.example", "phone_number": "+998000000000",
                      "phone_verified_at": timezone.now(), "language": data.validated_data["language"]},
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        # Never let a reserved-name collision turn into access to a real account.
        if (not user.is_active or user.is_deleted or user.is_staff or user.is_superuser or user.telegram_id is not None
                or user.role != "customer" or user.has_usable_password()
                or user.email != "local-preview@invalid.example" or user.phone_number != "+998000000000"):
            raise Http404
        record(user, "auth.local_preview_login", user)
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh), "user": ProfileSerializer(user).data})


class LocalPreviewInput(serializers.Serializer):
    language = serializers.ChoiceField(choices=["uz", "ru", "en"], default="uz")
