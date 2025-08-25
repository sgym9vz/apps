from datetime import datetime

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from matching_app.pkg.times import get_age_from_date_of_birth


class UserManager(BaseUserManager):
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        date_of_birth: datetime.date,
        **extra_fields: dict,
    ) -> "User":
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str,
        date_of_birth: datetime.date,
        **extra_fields: dict,
    ) -> "User":
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(
            username=username,
            email=email,
            password=password,
            date_of_birth=date_of_birth,
            **extra_fields,
        )
        return user


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=False)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(blank=False, null=False)
    icon = models.ImageField(upload_to="user_icons/", blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "date_of_birth"]


@receiver(post_save, sender=User)
def create_OneToOnes(instance, created, **kwargs):
    if created:
        from matching_app.models import UserProfile, UserVerification

        age = get_age_from_date_of_birth(instance.date_of_birth)
        UserProfile.objects.create(user=instance, age=age)
        user_verification = UserVerification.objects.create(user=instance)
        user_verification.send_new_verification_code()
