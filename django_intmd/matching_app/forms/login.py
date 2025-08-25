from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=50,
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
