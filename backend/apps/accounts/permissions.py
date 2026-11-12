from rest_framework.permissions import BasePermission


# Chỉ cho phép tài khoản Admin thực hiện thao tác quản trị.
class IsAdminRole(BasePermission):
    message = "Chỉ Admin mới được thực hiện thao tác này."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)