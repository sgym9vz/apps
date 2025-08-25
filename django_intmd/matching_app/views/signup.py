import structlog
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from matching_app.forms.signup import SignupForm
from matching_app.models.user import User

logger = structlog.get_logger(__name__)


@require_http_methods(["GET", "POST"])
def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SignupForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "signup.html",
                {"form": form},
            )

        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        date_of_birth = form.cleaned_data["date_of_birth"]
        user = User.objects.filter(email=email).first()
        if user is not None:
            if not user.is_active:
                user.delete()
            else:
                messages.error(request, "Email already registered.")
                logger.warning("email already registered", email=email)
                return render(request, "signup_error.html")

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                date_of_birth=date_of_birth,
                is_active=False,
            )

        if user is None:
            messages.error(request, "Sorry, failed to create user. Please try again.")
            logger.error("failed to create user", email=email)
            return render(request, "signup_error.html")

        login(request, user)
        return redirect("verify_email", id=user.id)

    else:
        form = SignupForm()

        return render(
            request,
            "signup.html",
            {"form": form},
        )
