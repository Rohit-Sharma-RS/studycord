import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message, Room, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        user_id = text_data_json['user_id']
        room_id = text_data_json['room_id']

        # Save message to database
        message_obj = await self.save_message(user_id, room_id, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'user_id': user_id,
                'message_id': message_obj.id,
                'timestamp': str(message_obj.created.strftime("%b %d, %Y, %I:%M %p"))
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))
        
    @database_sync_to_async
    def save_message(self, user_id, room_id, message):
        user = User.objects.get(id=user_id)
        room = Room.objects.get(id=room_id)
        
        # Add user to participants if not already there
        if user not in room.participants.all():
            room.participants.add(user)
            
        message_obj = Message.objects.create(
            user=user,
            room=room,
            body=message
        )
        return message_obj