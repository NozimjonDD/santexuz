from rest_framework import generics, permissions

from apps.api.v1.auth import serializers
from apps.users import models


class LoginAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    serializer_class = serializers.LoginSerializer
    model = models.User


class LoginConfirmAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    serializer_class = serializers.LoginConfirmSerializer
    model = models.User
