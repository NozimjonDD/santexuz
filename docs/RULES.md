# Instructions for Setting Up the Project

# Add .env file to the root of the project with the following content:

# Use scripts to make ready project for next steps:
-- set_permissions.sh
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# common shablon for create API views
class TBDeviceCreateAPIView(CreateAPIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [InternalPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # if u have file, use FormParser or MultiPartParser
    serializer_class = TBDeviceCreateSerializer
    queryset = TBDevice.objects.all()
   