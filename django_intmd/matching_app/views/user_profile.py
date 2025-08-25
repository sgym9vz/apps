import random

import structlog
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from matching_app.forms.user_profile import UserForm, UserProfileForm
from matching_app.models import UserLike

logger = structlog.get_logger(__name__)


@login_required
@require_http_methods(["GET"])
def user_home(request: HttpRequest) -> HttpResponse:
    return render(request, "user_home.html", {"user": request.user, "user_profile": request.user.userprofile})


@login_required
@require_http_methods(["GET", "POST"])
def user_profile_update(request: HttpRequest) -> HttpResponse:
    user_profile = request.user.userprofile

    if request.method == "POST":
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        is_valid = True
        if not user_form.is_valid():
            logger.error("Failed to update user icon", error=user_form.errors)
            is_valid = False
        if not user_profile_form.is_valid():
            logger.error("Failed to update user profile", error=user_profile_form.errors)
            is_valid = False
        if is_valid:
            user_form.save()
            user_profile_form.save()
            return redirect("user_home")
    else:
        user_form = UserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=user_profile)

    return render(
        request,
        "user_profile_update.html",
        {
            "user_form": user_form,
            "user_profile_form": user_profile_form,
            "user_profile": user_profile,
        },
    )


@login_required
@require_http_methods(["GET"])
def user_profile_list(request: HttpRequest) -> HttpResponse:
    users = list(get_user_model().objects.all().exclude(id=request.user.id))
    random.shuffle(users)
    return render(
        request,
        "user_profile_list.html",
        {"users": users},
    )


@login_required
@require_http_methods(["GET"])
def user_profile_detail(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(get_user_model().objects.select_related("userprofile"), pk=pk)
    is_like = UserLike.objects.filter(sender=request.user, receiver=user).exists()
    return render(
        request,
        "user_profile_detail.html",
        {"user": user, "is_like": is_like},
    )
