import structlog
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from matching_app.models.room import Room
from matching_app.models.room_member import RoomMember
from matching_app.pkg.exceptions import NoOppositeUserError

logger = structlog.get_logger(__name__)


@login_required
@require_http_methods(["GET"])
def chat_room(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room, pk=room_id)

    if not RoomMember.is_member(room, request.user):
        logger.warning("invalid room access", user=request.user, room=room)
        raise PermissionDenied

    try:
        opposite_user = room.get_opposite_user(current_user=request.user)
    except NoOppositeUserError as ex:
        logger.error("no opposite user", error=ex)
        return HttpResponseServerError()

    return render(
        request,
        "chat_room.html",
        {
            "room": room,
            "user": request.user,
            "opposite_user": opposite_user,
        },
    )


@login_required
@require_http_methods(["POST"])
def chat_room_create(request: HttpRequest, user_id: int) -> HttpResponse:
    opposite_user = get_object_or_404(get_user_model(), pk=user_id)
    try:
        room = Room.objects.get_or_create_room_with_members([request.user, opposite_user])
    except ValidationError as ex:
        logger.error("failed to create chat room", error=ex)
        return HttpResponseServerError()

    return redirect("chat_room", room_id=room.id)

@login_required
@require_http_methods(["GET"])
def chat_room_list(request: HttpRequest) -> HttpResponse:
    room_members = RoomMember.objects.filter(user=request.user).select_related("room")

    room_data_dict = {}
    for room_member in room_members:
        room = room_member.room
        try:
            opposite_user = room.get_opposite_user(current_user=request.user)
        except NoOppositeUserError as ex:
            logger.error("no opposite user", room=room, error=ex)
            return HttpResponseServerError()

        last_message = room.messages.order_by("-created_at").first()
        room_data_dict[room] = {
            "opposite_user": opposite_user,
            "last_message": last_message,
        }

    return render(
        request,
        "chat_room_list.html",
        {"room_data_dict": room_data_dict, "user": request.user},
    )
