# accounts/urls.py
from django.urls import path
# from .views import signup
from . import views


urlpatterns = [
    path("check/username/", views.check_username),

    path("signup/", views.signup, name="signup"),

    path("user-details/", views.user_details, name='user_details'),
]

