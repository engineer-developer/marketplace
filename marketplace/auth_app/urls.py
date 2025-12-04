from django.urls import path

from auth_app.views import (
    SignInView,
    SignOutView,
    RegistrationView,
)


app_name = "auth_app"

urlpatterns = [
    path("sign-in", SignInView.as_view(), name="sign_in"),
    path("sign-out", SignOutView.as_view(), name="sign_out"),
    path("sign-up", RegistrationView.as_view(), name="sign_up"),
]
