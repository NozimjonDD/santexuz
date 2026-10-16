from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny


class MyAPIView(ListAPIView):
    """
    Example API view that lists items.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        # Replace with your actual queryset logic
        return []
