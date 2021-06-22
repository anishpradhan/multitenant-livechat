"""
ASGI config for livechat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from .wsgi import *
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chat.routing as routing
from chat.utils import ChatMTMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livechat.settings')

application = ProtocolTypeRouter({
    "websocket": ChatMTMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
})
