from django import forms

from accounts.models import CustomUser


class UserManageForm(forms.ModelForm):
    """What an admin may change about another user: their role and whether they can log in."""

    class Meta:
        model = CustomUser
        fields = ("role", "is_active")
        labels = {"is_active": "Account is active (can log in)"}
