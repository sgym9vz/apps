import structlog
from django.core.exceptions import ValidationError
from django.db import models, transaction

from matching_app.models.base import BaseModel
from matching_app.models.room_member import RoomMember
from matching_app.models.user import User
from matching_app.pkg.exceptions import NoOppositeUserError

logger = structlog.get_logger(__name__)

MAX_ROOM_MEMBERS = 2


class RoomManager(models.Manager):
    def get_or_create_room_with_members(self, users: list[User]) -> "Room":
        if len(users) != MAX_ROOM_MEMBERS:
            logger.error("invalid number of users", users=users)
            raise ValidationError(f"Room must have exactly {MAX_ROOM_MEMBERS} members")

        user_ids = sorted(user.id for user in users)

        try:
            existing_room = self.filter(members__user_id=user_ids[0]).filter(members__user_id=user_ids[1]).first()
        except IndexError as ex:
            logger.error("invalid user ids", user_ids=user_ids, error=ex)
            raise ValidationError("Invalid user ids")

        if existing_room:
            return existing_room

        with transaction.atomic():
            room = self.create()
            for user in users:
                RoomMember.objects.create(room=room, user=user)
        return room


class Room(BaseModel):
    objects = RoomManager()

    class Meta:
        ordering = ["-updated_at"]

    def get_opposite_user(self, current_user: User) -> User:
        opposite_member = self.members.exclude(user=current_user).select_related("user").first()
        if not opposite_member:
            logger.error("no opposite member", room=self)
            raise NoOppositeUserError("no opposite member")
        return opposite_member.user

    def __str__(self):
        return f"Room {self.id} with members {self.members.all()}"
