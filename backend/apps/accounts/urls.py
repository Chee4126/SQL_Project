from django.urls import path

from apps.accounts.views import (
    LoginView,
    LogoutView,
    MeView,
    UserListCreateView,
    UserRoleView,
)

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/me", MeView.as_view(), name="auth-me"),
    path("admin/users", UserListCreateView.as_view(), name="admin-user-list-create"),
    path(
        "admin/users/<int:user_id>/role",
        UserRoleView.as_view(),
        name="admin-user-role",
    ),
]