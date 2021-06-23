from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message, Room
from .views import *
from channels.db import database_sync_to_async

User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        print(self.scope['user'])
        print(self.scope)
        self.schema_name = self.scope.get('schema_name', None)
        # self.schema_name = 't1'
        self.multitenant = self.scope.get('multitenant', False)

        self.room_id = self.scope['url_route']['kwargs']['room_uuid']

        try:

            self.room = get_room(self.room_id, self.multitenant, self.schema_name)

            # if self.room.ended is not None:
            #     self.disconnect(close_code=500)
            if self.multitenant:
                from django_tenants.utils import schema_context
                with schema_context(self.schema_name):
                    self.room_group_name = 'chat_%s' % self.room_id
                    async_to_sync(self.channel_layer.group_add)(
                        self.room_group_name,
                        self.channel_name
                    )
                    user_contact = get_user_contact(self.scope['user'], self.multitenant, self.schema_name)
                    if user_contact:
                        user = self.scope['user']
                    else:
                        user = self.room.name
                    message = f'{user} joined the chat.'
                    content = {
                        'command': 'joined_chat',
                        'message': message,
                    }
                    self.send_chat_message(content)
                    self.accept()
            else:
                self.disconnect(500)

        except Exception as ex:
            raise ex
            self.disconnect(500)

    def disconnect(self, close_code):
        # current_chat = get_room(self.scope['url_route']['kwargs']['room_uuid'], self.multitenant, self.schema_name)
        # current_chat.end()
        # current_chat.save()
        # user_contact = get_user_contact(self.scope['user'], self.multitenant, self.schema_name)
        # if user_contact:
        #     user = self.scope['user']
        # else:
        #     user = get_room(self.room_id, self.multitenant, self.schema_name)
        #     user = user.name
        # message = f'{user} left the chat. This chat has ended'
        # content = {
        #     'command': 'end_chat',
        #     'message': message,
        # }
        # self.send_chat_message(content)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    # async def fetch_messages(self, data):
    #     messages = get_last_10_messages(data['chatId'])
    #     content = {
    #         'command': 'messages',
    #         'messages': self.messages_to_json(messages)
    #     }
    #     await self.send_message(content)

    def new_message(self, data):
        user_contact = get_user_contact(data['from'], self.multitenant, self.schema_name)
        current_chat = get_room(data['chatId'], self.multitenant, self.schema_name)
        if user_contact:
            message = Message.objects.create(
                room=current_chat,
                agent=user_contact,
                message=data['message'])
        else:
            message = Message.objects.create(
                room=current_chat,
                message=data['message'])
        message.save()
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message),
        }
        return self.send_chat_message(content)

    def end_chat(self, data):
        current_chat = get_room(data['chatId'], self.multitenant, self.schema_name)
        current_chat.end()
        current_chat.save()
        name = data['left']
        message = '%s has left the chat.  This chat has ended.' % name
        content = {
            'command': 'end_chat',
            'message': message,
        }
        return self.send_chat_message(content)

    def upload_file(self, data):
        uploaded_by = get_user_contact(data['uploaded_by'], self.multitenant, self.schema_name)
        file = get_file_by_id(data['file_id'], self.multitenant, self.schema_name)
        current_chat = get_room(data['chatId'], self.multitenant, self.schema_name)
        if uploaded_by:
            message = Message.objects.create(
                room=current_chat,
                agent=uploaded_by,
                file=file)
        else:
            message = Message.objects.create(
                room=current_chat,
                file=file)
        message.save()
        content = {
            'command': 'uploaded_file',
            'message': {
                'id': str(message.id),
                'uploaded_by': data['uploaded_by'],
                'file_id': str(message.file.id),
                'file_name': message.file.get_file_name(),
                'timestamp': str(message.sent)
            }
        }
        return self.send_chat_message(content)

    def is_typing(self, data):
        content = {
            'command': 'is_typing',
            'message': {
                'by': data['by'],
            }
        }
        return self.send_chat_message(content)

    def finished_typing(self, data):
        content = {
            'command': 'finished_typing',
            'message': {
                'by': data['by'],
            }
        }
        return self.send_chat_message(content)

    commands = {
        # 'fetch_messages': fetch_messages,
        'upload_file': upload_file,
        'new_message': new_message,
        'end_chat': end_chat,
        'is_typing': is_typing,
        'finished_typing': finished_typing,
    }

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        try:
            return {
                'id': str(message.id),
                'author': message.agent.username,
                'content': message.message,
                'timestamp': str(message.sent)
            }
        except:
            return {
                'id': str(message.id),
                'author': message.room.name,
                'content': message.message,
                'timestamp': str(message.sent)
            }

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
