from django import forms
from django.core.exceptions import ValidationError

from matching_app.models import Recruitment


class RecruitmentForm(forms.ModelForm):
    class Meta:
        model = Recruitment
        fields = ["title", "content"]
        exclude = ["user"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Enter your title",
                    "id": "title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "input",
                    "placeholder": "Enter your content",
                    "id": "content",
                }
            ),
        }


class SearchRecruitmentForm(forms.Form):
    min_age = forms.IntegerField(
        required=False,
        label="Min Age",
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": "Min Age", "id": "min_age"}),
    )
    max_age = forms.IntegerField(
        required=False,
        label="Max Age",
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": "Max Age", "id": "max_age"}),
    )

    def clean(self):
        cleaned_data = super().clean()

        min_age = cleaned_data.get("min_age")
        max_age = cleaned_data.get("max_age")
        if (min_age and min_age < 18) or (max_age and max_age < 18):
            raise ValidationError("Age must be over 18")
        if min_age and max_age and min_age > max_age:
            raise ValidationError("Min age must be less than max age")

        return cleaned_data
