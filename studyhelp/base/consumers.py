import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        user_id = data['user_id']

        # Broadcast to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'user_id': user_id,
            }
        )

    # Receive message from group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
        }))