from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from matching_app.channels.chat_consumer import ChatConsumer
from matching_app.models.room import Room


class ChatConsumerTests(TransactionTestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username="chat_user1",
            email="chat1@example.com",
            password="Chat1Pass123",
            date_of_birth="2000-01-01",
        )
        self.user2 = get_user_model().objects.create_user(
            username="chat_user2",
            email="chat2@example.com",
            password="Chat2Pass123",
            date_of_birth="2000-01-01",
        )
        self.room = Room.objects.get_or_create_room_with_members([self.user1, self.user2])

    async def test_connect(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.room.id}/",
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {"kwargs": {"room_id": self.room.id}}
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_receive_message(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.room.id}/",
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {"kwargs": {"room_id": self.room.id}}
        await communicator.connect()

        message_data = {
            "type": "chat.message",
            "sender_id": self.user1.id,
            "room_id": self.room.id,
            "message": "New test message",
        }
        await communicator.send_json_to(message_data)
        response = await communicator.receive_json_from()

        self.assertEqual(response["message"], "New test message")
        self.assertEqual(response["sender"], self.user1.username)
