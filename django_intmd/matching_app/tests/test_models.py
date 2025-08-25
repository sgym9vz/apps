from django.contrib.auth import get_user_model
from django.test import TestCase

from matching_app.models import Message, Room


class UserModelsTestCase(TestCase):
    def test_create_user_success(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",
            date_of_birth="2000-01-01",
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.date_of_birth, "2000-01-01")

        user.delete()

    def test_create_superuser_success(self):
        superuser = get_user_model().objects.create_superuser(
            username="testsuperuser",
            email="test@example.com",
            password="password",
            date_of_birth="2000-01-01",
        )

        self.assertEqual(superuser.username, "testsuperuser")
        self.assertEqual(superuser.email, "test@example.com")
        self.assertEqual(superuser.date_of_birth, "2000-01-01")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

        superuser.delete()


class BaseModelsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",
            date_of_birth="2000-01-01",
        )
        self.user2 = get_user_model().objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="password",
            date_of_birth="2000-01-01",
        )


class RoomModelsTestCase(BaseModelsTestCase):
    def test_create_room_success(self):
        room = Room.objects.get_or_create_room_with_members([self.user, self.user2])

        self.assertIsNotNone(room.id)
        self.assertEqual(room.members.count(), 2)
        self.assertEqual(room.members.filter(id=self.user.id).count(), 1)
        self.assertEqual(room.members.filter(id=self.user2.id).count(), 1)


class MessageModelsTestCase(BaseModelsTestCase):
    def test_create_message_success(self):
        room = Room.objects.get_or_create_room_with_members([self.user, self.user2])
        message = Message.objects.create(
            sender=self.user,
            room=room,
            content="Hello, world!",
        )

        self.assertEqual(message.sender, self.user)
        self.assertEqual(message.room, room)
        self.assertEqual(message.content, "Hello, world!")
