import json

import structlog
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from matching_app.models.message import Message
from matching_app.models.room import Room

logger = structlog.get_logger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        try:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        except Exception as ex:
            logger.error("Failed to connect to chat room", error=ex)
            await self.close()
            return

        try:
            await self.accept()
        except Exception as ex:
            logger.error("Failed to accept connection", error=ex)
            await self.close()
            return

        message_history = await self.get_message_history(self.room_id)
        for message in message_history:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": message.content,
                        "sender": message.sender.username,
                        "created_at": message.created_at.isoformat(),
                    }
                )
            )

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.delete_empty_room()

    async def receive(self, text_data: str) -> None:
        decoded_text_data = json.loads(text_data)

        required_fields = ["sender_id", "room_id", "message"]
        for field in required_fields:
            if field not in decoded_text_data:
                logger.error("Missing required field", field=field)
                return

        if not decoded_text_data["message"].strip():
            logger.warning("Empty message received")
            return

        try:
            message = await self.create_message(
                decoded_text_data["sender_id"], decoded_text_data["room_id"], decoded_text_data["message"]
            )
        except Exception as ex:
            logger.error("Failed to create message", error=ex)
            return

        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message.content,
                    "sender": message.sender.username,
                    "created_at": message.created_at.isoformat(),
                },
            )
        except Exception as ex:
            logger.error("Failed to send message to group", error=ex)
            return

    async def chat_message(self, event: dict) -> None:
        required_fields = ["message", "sender", "created_at"]
        for field in required_fields:
            if field not in event:
                logger.error("Missing required field", field=field)
                return

        try:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": event["message"],
                        "sender": event["sender"],
                        "created_at": event["created_at"],
                    }
                )
            )
        except Exception as ex:
            logger.error("Failed to send message to client", error=ex)
            return

    @database_sync_to_async
    def get_message_history(self, room_id: int) -> list[Message]:
        return list(Message.objects.filter(room_id=room_id).select_related("sender").order_by("created_at"))

    @database_sync_to_async
    def create_message(self, sender_id: int, room_id: int, content: str) -> Message:
        sender = get_user_model().objects.get(pk=sender_id)
        room = Room.objects.get(pk=room_id)
        return Message.objects.create(
            sender=sender,
            room=room,
            content=content,
        )

    @database_sync_to_async
    def delete_empty_room(self) -> None:
        room = Room.objects.get(pk=self.room_id)
        if not Message.objects.filter(room=room).exists():
            room.delete()
