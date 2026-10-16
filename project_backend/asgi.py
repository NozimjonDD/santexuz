import os

from dotenv import load_dotenv

load_dotenv()

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv("DJANGO_SETTINGS_MODULE"))

application = get_asgi_application()

'''ASGI config for project_backend project.'''
# wsgi_application = get_asgi_application()
#
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# from .middleware import JWTAuthMiddlewareStack
#
# from api.v1.websocket.routing import websocket_urlpatterns
#
# application = ProtocolTypeRouter(
#     {
#         "http": wsgi_application,
#         "websocket": AllowedHostsOriginValidator(
#             JWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
#         ),
#     }
# )
