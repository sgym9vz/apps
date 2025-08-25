from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectDateWidget

from matching_app.pkg.times import MAX_BIRTH_YEAR, MIN_BIRTH_YEAR, is_over_18_years_old


class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Your name",
                "id": "name",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "placeholder": "example@email.com",
                "id": "email",
            }
        ),
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "placeholder": "Input your password",
                "id": "password",
            }
        ),
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=SelectDateWidget(
            years=range(MIN_BIRTH_YEAR, MAX_BIRTH_YEAR + 1),
            attrs={"class": "date-select-row"},
        ),
    )

    def clean_password(self) -> str:
        password = self.cleaned_data.get("password")
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e)
        return password

    def clean(self) -> dict:
        cleaned_data = super().clean()

        date_of_birth = cleaned_data.get("date_of_birth")

        if not is_over_18_years_old(date_of_birth):
            raise ValidationError("Must be over 18 years old")

        cleaned_data["date_of_birth"] = date_of_birth
        return cleaned_data
