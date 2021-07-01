"""
ASGI config for livechat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from channels.layers import get_channel_layer
from .wsgi import *
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livechat.settings')
channel_layers = get_channel_layer()
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chat.routing as routing
from chat.utils import ChatMTMiddlewareStack



application = ProtocolTypeRouter({
    "websocket": ChatMTMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
})
