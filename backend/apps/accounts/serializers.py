from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

ADMIN = "ADMIN"
STAFF = "STAFF"
ROLE_CHOICES = [ADMIN, STAFF]


# Nhận thông tin đăng nhập.
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# Hiển thị tài khoản kèm vai trò (không bao giờ trả mật khẩu).
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="first_name", read_only=True)
    role = serializers.SerializerMethodField()

    # Khai báo các trường tài khoản trả về qua API.
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "role", "is_active"]

    def get_role(self, obj):
        return ADMIN if obj.is_superuser else STAFF


# Kiểm tra dữ liệu khi Admin tạo tài khoản mới.
class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, default=STAFF)

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên đăng nhập không được để trống.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Tên đăng nhập đã tồn tại.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("full_name", ""),
        )
        if validated_data["role"] == ADMIN:
            user.is_superuser = True
            user.is_staff = True
            user.save(update_fields=["is_superuser", "is_staff"])
        return user


# Nhận vai trò mới khi Admin đổi quyền.
class RoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=ROLE_CHOICES)