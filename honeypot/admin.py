from django.contrib import admin
from .models import LoginAttempt


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'ip_address',
        'created_at',
    )

    list_filter = (
        'created_at',
    )

    search_fields = (
        'username',
        'ip_address',
    )

    ordering = (
        '-created_at',
    )

    readonly_fields = (
        'created_at',
    )