from django.urls import path, include
from . import views
from . import api

urlpatterns = [
    path('', views.index, name="index"),
    path('support/', views.admin_index, name="admin_index"),
    path('admin_join_chat/<str:room_id>', views.join_chat, name="admin_join_chat"),
    path('admin_end_chat/<str:room_id>', views.end_chat, name="admin_end_chat"),
    path('support/chat_page/<str:room_id>', views.chat_page, name="chat_page"),
    path('client/chat_page/<str:room_id>', views.client_chat_page, name="client_chat_page"),
    path('ajax/', views.ajax_create_room, name="ajax_create_room"),
    path('ajax/get_support_groups/', views.get_support_groups, name="get_support_groups"),
    path('api/create_room/', api.create_room, name="create_room"),
    path('api/upload_file/', api.fileUpload, name="upload_file"),


    ]