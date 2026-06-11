import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Comment
from .serializers import CommentSerializer


class CommentConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "comments"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        comment = await self.save_comment(data)
        if comment is None:
            await self.send(text_data=json.dumps({"error": "Невалідні дані."}))
            return

        serialized = await self.serialize_comment(comment)
        await self.channel_layer.group_send(
            self.GROUP_NAME,
            {"type": "broadcast_comment", "comment": serialized},
        )

    async def broadcast_comment(self, event):
        await self.send(text_data=json.dumps(event["comment"]))

    @database_sync_to_async
    def save_comment(self, data):
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        return None

    @database_sync_to_async
    def serialize_comment(self, comment):
        return CommentSerializer(comment).data
