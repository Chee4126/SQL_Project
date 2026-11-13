from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import (
    LoginSerializer,
    ProfileUpdateSerializer,
    RegistrationSerializer,
    UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()


# Đăng nhập bằng email và mật khẩu, trả về token.
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = User.objects.filter(
            email__iexact=serializer.validated_data["email"].strip()
        ).first()
        user = None
        if account:
            user = authenticate(
                request,
                username=account.username,
                password=serializer.validated_data["password"],
            )
        if user is None:
            return Response(
                {"detail": "Sai tên đăng nhập hoặc mật khẩu."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


# Đăng ký tài khoản Staff và đăng nhập ngay sau khi tạo.
class RegistrationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


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

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_data = UserSerializer(user).data
        if serializer.validated_data.get("new_password"):
            Token.objects.filter(user=user).delete()
            response_data["token"] = Token.objects.create(user=user).key
        return Response(response_data)


# Staff xem danh sách và tạo tài khoản Staff.
class AccountListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.order_by("email")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class AccountDetailView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    lookup_url_kwarg = "user_id"

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError(
                {"detail": "Không thể xóa tài khoản đang đăng nhập."}
            )
        instance.delete()