from django import forms

from matching_app.models.user import User
from matching_app.models.user_profile import UserProfile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "icon"]
        exclude = ["email", "date_of_birth"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Enter your username",
                }
            ),
            "icon": forms.FileInput(
                attrs={
                    "class": "icon-input",
                    "placeholder": "Choose an icon",
                }
            ),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["address", "occupation", "biography"]
        exclude = ["user", "age"]
        widgets = {
            "address": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Enter your address",
                    "id": "address",
                }
            ),
            "occupation": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Enter your occupation",
                    "id": "occupation",
                }
            ),
            "biography": forms.Textarea(
                attrs={
                    "class": "input",
                    "placeholder": "Enter your biography",
                    "id": "biography",
                }
            ),
        }
