from django.contrib.auth import get_user_model
from django.db import models

from matching_app.models.base import BaseModel


class UserProfile(BaseModel):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    age = models.IntegerField(blank=False, null=False, default=0)
    address = models.CharField(max_length=100, blank=True, null=False)
    occupation = models.CharField(max_length=100, blank=True, null=False)
    biography = models.TextField(blank=True, null=False)

    def __str__(self):
        return self.user.username
