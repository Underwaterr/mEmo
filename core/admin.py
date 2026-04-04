from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Event, Poll, PollDateOption, PollInvitation, PollResponse, User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "display_name", "email", "is_staff"]
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Band Info", {"fields": ("display_name",)}),
    )
    fieldsets = UserAdmin.fieldsets + (
        ("Band Info", {"fields": ("display_name",)}),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "date", "type", "status"]


class PollDateOptionInline(admin.TabularInline):
    model = PollDateOption
    extra = 1

class PollInvitationInline(admin.TabularInline):
    model = PollInvitation
    extra = 1


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ["title", "deadline", "closed"]
    inlines = [PollDateOptionInline, PollInvitationInline]

