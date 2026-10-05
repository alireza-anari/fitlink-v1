import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django_application = get_asgi_application()
if os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings.development":
    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

    django_application = ASGIStaticFilesHandler(django_application)

from .routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
