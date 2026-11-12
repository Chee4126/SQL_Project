from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from apps.accounts.serializers import (
    ADMIN,
    LoginSerializer,
    RoleUpdateSerializer,
    UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()


# Đăng nhập bằng tên đăng nhập và mật khẩu, trả về token.
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"detail": "Sai tên đăng nhập hoặc mật khẩu."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


# Đăng xuất bằng cách xóa token hiện tại.
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.auth is not None:
            request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Lấy thông tin tài khoản đang đăng nhập.
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# Admin xem danh sách và tạo tài khoản nhân viên.
class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.order_by("username")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


# Admin đổi vai trò của một tài khoản.
class UserRoleView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data["role"]
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFound("Không tìm thấy tài khoản.")
        if user.pk == request.user.pk and role != ADMIN:
            raise ValidationError({"role": "Không thể tự hạ quyền của chính mình."})
        user.is_superuser = role == ADMIN
        user.is_staff = role == ADMIN
        user.save(update_fields=["is_superuser", "is_staff"])
        return Response(UserSerializer(user).data)