from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.tg_bot.models import Notification
from apps.tg_bot.services import notification_text


class NotificationSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    def get_text(self, obj) -> str:
        return notification_text(obj)

    class Meta:
        model = Notification
        fields = ["id", "event", "order_id", "text", "created_at", "read_at"]


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user).select_related("user")


class NotificationReadView(generics.GenericAPIView):
    serializer_class = NotificationSerializer

    @extend_schema(request=None, responses=NotificationSerializer)
    def post(self, request, pk):
        item = get_object_or_404(Notification, pk=pk, user=request.user)
        if not item.read_at:
            item.read_at = timezone.now()
            item.save(update_fields=["read_at"])
        return Response(NotificationSerializer(item).data)
