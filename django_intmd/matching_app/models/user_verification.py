from datetime import timedelta
from random import randint

import django.utils.timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string

from matching_app.models.base import BaseModel
from matching_app.pkg.times import calculate_expiration_time

VERIFICATION_CODE_LENGTH = 6
MIN_VERIFICATION_CODE = 10 ** (VERIFICATION_CODE_LENGTH - 1)
MAX_VERIFICATION_CODE = (10**VERIFICATION_CODE_LENGTH) - 1
DEFAULT_VERIFICATION_EXPIRATION_MINUTES = 60


class UserVerification(BaseModel):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=VERIFICATION_CODE_LENGTH, null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username

    def set_new_verification_code(self) -> None:
        self.verification_code = randint(MIN_VERIFICATION_CODE, MAX_VERIFICATION_CODE)

    def set_expiration(self, expiration_minutes: int = DEFAULT_VERIFICATION_EXPIRATION_MINUTES) -> None:
        self.expired_at = calculate_expiration_time(django.utils.timezone.now(), timedelta(minutes=expiration_minutes))

    def is_expired(self) -> bool:
        return django.utils.timezone.now() > self.expired_at

    def send_verification_code(self) -> None:
        send_mail(
            subject="Your verification code",
            message=render_to_string("emails/signup_verification.txt", {"user": self.user, "user_verification": self}),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
        )

    def send_new_verification_code(self) -> None:
        self.set_new_verification_code()
        self.set_expiration()
        self.save()
        self.send_verification_code()
