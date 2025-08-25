from django import forms

from matching_app.models.user_verification import VERIFICATION_CODE_LENGTH


class VerifyEmailForm(forms.Form):
    verification_code = forms.CharField(max_length=VERIFICATION_CODE_LENGTH)
