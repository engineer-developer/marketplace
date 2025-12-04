from django.urls import path

from profile_app.views import AvatarAPIView, ProfileAPIView, UpdateUserPasswordAPIView


app_name = "profile_app"

urlpatterns = [
    path("profile/avatar", AvatarAPIView.as_view(), name="user_avatar_create"),
    path("profile", ProfileAPIView.as_view(), name="user_profile"),
    path(
        "profile/password", UpdateUserPasswordAPIView.as_view(), name="update_password"
    ),
]
