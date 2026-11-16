from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["email", "username", "role", "is_staff"]
    ordering = ["email"]
    fieldsets = UserAdmin.fieldsets + (("OmniRead", {"fields": ("role", "contact_number")}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("email", "role")}),)
