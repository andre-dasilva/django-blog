from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, EmailField, CharField
from rest_framework_jwt.settings import api_settings

User = get_user_model()


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]


class UserCreateSerializer(ModelSerializer):
    email = EmailField()
    confirm_email = EmailField()

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "confirm_email",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        email = data.get("email")
        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            raise ValidationError("Mail already exists")
        return data

    def validate_confirm_email(self, value):
        data = self.get_initial()
        email = data.get("email")
        confirm_email = value

        if email != confirm_email:
            raise ValidationError("Emails must match")

        return value

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")
        user_obj = User(username=username, email=email)
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "password",
            "email"
        ]


class UserLoginSerializer(ModelSerializer):
    token = CharField(allow_blank=True, read_only=True)
    username = CharField(allow_blank=True, required=False)
    email = EmailField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "token"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        email = data.get("email", None)
        username = data.get("username", None)
        password = data.get("password")

        if not email and not username:
            raise ValidationError("A username or email is required to login")

        user = User.objects.filter(
            Q(email=email) |
            Q(username=username)
        ).distinct().exclude(email__isnull=True).exclude(email__iexact="")

        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError("This username / email is not valid")

        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect credentials")

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user_obj)
        token = jwt_encode_handler(payload)

        data["token"] = token
        return data

