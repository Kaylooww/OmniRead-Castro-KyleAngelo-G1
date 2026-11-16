from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

FIELDS = ("email", "username", "first_name", "last_name", "contact_number")


class AccountFieldsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name"):
            self.fields[name].required = True

    def clean_email(self):
        # Store emails lowercase so the unique check also catches "A@x.com" vs "a@x.com"
        return self.cleaned_data["email"].lower()


class SignUpForm(AccountFieldsMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = FIELDS


class ProfileForm(AccountFieldsMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = FIELDS
