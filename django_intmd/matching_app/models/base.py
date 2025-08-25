from django.db import models

# import User because let django recognize custom user models.
from matching_app.models.user import User  # noqa F401


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
