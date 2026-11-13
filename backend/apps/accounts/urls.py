from django.urls import path

from apps.accounts.views import (
    LoginView,
    LogoutView,
    MeView,
    RegistrationView,
    AccountListCreateView,
    AccountDetailView,
)

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/register", RegistrationView.as_view(), name="auth-register"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/me", MeView.as_view(), name="auth-me"),
    path("accounts", AccountListCreateView.as_view(), name="account-list-create"),
    path("accounts/<int:user_id>", AccountDetailView.as_view(), name="account-detail"),
]