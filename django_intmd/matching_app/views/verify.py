import structlog
from django.contrib.auth import get_user_model, login
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from matching_app.forms.verify import VerifyEmailForm
from matching_app.models.user_verification import UserVerification

logger = structlog.get_logger(__name__)


@require_http_methods(["POST", "GET"])
def verify_email(request: HttpRequest, id: int) -> HttpResponse:
    user = get_object_or_404(get_user_model(), id=id)

    if request.method == "POST":
        form = VerifyEmailForm(request.POST)
        if not form.is_valid():
            logger.warning("invalid form", user=user, error=form.errors)
            return render(request, "verify_email.html", {"form": form, "id": id})

        input_code = form.cleaned_data["verification_code"]
        user_verification = user.userverification

        if input_code != user_verification.verification_code:
            logger.warning(
                "invalid verification code",
                user=user,
                input_code=input_code,
                user_verification_code=user_verification.verification_code,
            )
            form.add_error("verification_code", "Invalid verification code.")
            return render(request, "verify_email.html", {"form": form, "id": id})

        if user_verification.is_expired():
            logger.warning("verification code is expired", user=user)
            form.add_error("verification_code", "Verification code is expired. Please request a new one.")
            return render(request, "verify_email.html", {"form": form, "id": id})

        with transaction.atomic():
            user.is_active = True
            user.save()
            user_verification.delete()
        login(request, user)
        return redirect("user_home")

    else:
        form = VerifyEmailForm()
        return render(request, "verify_email.html", {"form": form, "id": id})


def send_new_verification_code(request: HttpRequest, id: int) -> HttpResponse:
    user = get_object_or_404(get_user_model(), id=id)
    user_verification, _ = UserVerification.objects.get_or_create(user=user)
    user_verification.send_new_verification_code()

    return redirect("verify_email", id=id)
