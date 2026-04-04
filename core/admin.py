from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "display_name", "email", "is_staff"]
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Band Info", {"fields": ("display_name",)}),
    )
    fieldsets = UserAdmin.fieldsets + (
        ("Band Info", {"fields": ("display_name",)}),
    )
