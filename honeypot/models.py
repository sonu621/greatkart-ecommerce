from django.db import models


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=255)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username