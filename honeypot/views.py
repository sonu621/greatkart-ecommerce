from django.shortcuts import render
from .models import LoginAttempt


def fake_admin(request):

    if request.method == "POST":

        LoginAttempt.objects.create(
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    return render(
        request,
        "honeypot/login.html"
    )