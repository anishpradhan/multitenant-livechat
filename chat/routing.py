from django.urls import path
# from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    path('ws/livechat/chatrooms/<str:room_uuid>/', consumers.ChatConsumer.as_asgi()),
]