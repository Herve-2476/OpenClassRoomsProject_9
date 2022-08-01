from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views


urlpatterns = [
    path("signup/", views.signup_page, name="signup"),
    path(
        "",
        LoginView.as_view(template_name="authentication/login.html", redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
