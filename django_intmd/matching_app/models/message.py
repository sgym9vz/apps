from django.contrib.auth import get_user_model
from django.db import models

from matching_app.models.base import BaseModel
from matching_app.models.room import Room


class Message(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"{self.sender.username} - {self.content[:20]}"
