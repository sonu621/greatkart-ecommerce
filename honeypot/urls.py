from django.urls import path
from .views import fake_admin

urlpatterns = [
    path("", fake_admin, name="fake_admin"),
]