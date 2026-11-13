from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import UserProfile

User = get_user_model()

STAFF = "STAFF"


# Nhận thông tin đăng nhập.
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


def validate_email(value):
    email = value.strip().lower()
    if User.objects.filter(email__iexact=email).exists():
        raise serializers.ValidationError("Email đã được sử dụng.")
    return email


def validate_phone_number(value):
    phone_number = value.strip()
    digit_count = sum(character.isdigit() for character in phone_number)
    if not 7 <= digit_count <= 15:
        raise serializers.ValidationError("Số điện thoại phải có từ 7 đến 15 chữ số.")
    return phone_number


def username_from_email(email):
    base = email.partition("@")[0][:150]
    username = base
    suffix = 2
    while User.objects.filter(username__iexact=username).exists():
        username = f"{base[: 150 - len(str(suffix))]}{suffix}"
        suffix += 1
    return username


# Đăng ký tài khoản Staff; vai trò không nhận từ dữ liệu client.
class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    full_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    validate_email = staticmethod(validate_email)
    validate_phone_number = staticmethod(validate_phone_number)

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Họ tên không được để trống.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Mật khẩu xác nhận không khớp."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        phone_number = validated_data.pop("phone_number")
        full_name = validated_data.pop("full_name")
        email = validated_data["email"]
        user = User.objects.create_user(
            username=username_from_email(email),
            email=email,
            password=password,
            first_name=full_name,
        )
        UserProfile.objects.create(user=user, phone_number=phone_number)
        return user


# Hiển thị tài khoản kèm vai trò (không bao giờ trả mật khẩu).
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="first_name", read_only=True)
    role = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    # Khai báo các trường tài khoản trả về qua API.
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "full_name",
            "role",
            "is_active",
        ]

    def get_role(self, obj):
        return STAFF

    def get_phone_number(self, obj):
        try:
            return obj.account_profile.phone_number
        except UserProfile.DoesNotExist:
            return ""


# Kiểm tra dữ liệu khi Staff tạo tài khoản mới.
class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    full_name = serializers.CharField(max_length=150)
    validate_email = staticmethod(validate_email)
    validate_phone_number = staticmethod(validate_phone_number)

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Họ tên không được để trống.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number")
        full_name = validated_data.pop("full_name")
        password = validated_data.pop("password")
        email = validated_data["email"]
        user = User.objects.create_user(
            username=username_from_email(email),
            email=email,
            password=password,
            first_name=full_name,
        )
        UserProfile.objects.create(user=user, phone_number=phone_number)
        return user


class ProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    phone_number = serializers.CharField(max_length=20)
    current_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        min_length=6,
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    validate_phone_number = staticmethod(validate_phone_number)

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Họ tên không được để trống.")
        return value

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        ).exists():
            raise serializers.ValidationError("Email đã được sử dụng.")
        return email

    def validate(self, attrs):
        current_password = attrs.get("current_password", "")
        new_password = attrs.get("new_password", "")
        password_confirm = attrs.get("password_confirm", "")

        if new_password or password_confirm:
            if not current_password:
                raise serializers.ValidationError(
                    {"current_password": "Vui lòng nhập mật khẩu hiện tại."}
                )
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError(
                    {"current_password": "Mật khẩu hiện tại không chính xác."}
                )
            if new_password != password_confirm:
                raise serializers.ValidationError(
                    {"password_confirm": "Mật khẩu xác nhận không khớp."}
                )
        elif current_password:
            raise serializers.ValidationError(
                {"new_password": "Vui lòng nhập mật khẩu mới để đổi mật khẩu."}
            )

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        new_password = validated_data.pop("new_password", "")
        validated_data.pop("current_password", None)
        validated_data.pop("password_confirm", None)

        instance.first_name = validated_data["full_name"]
        instance.email = validated_data["email"]
        if new_password:
            instance.set_password(new_password)
        instance.save(update_fields=["first_name", "email", "password"])

        UserProfile.objects.update_or_create(
            user=instance,
            defaults={"phone_number": validated_data["phone_number"]},
        )
        return instance