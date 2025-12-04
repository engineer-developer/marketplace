from django.contrib.auth.models import User
from rest_framework import serializers
from drf_spectacular import utils

from mainsite.main_logger import logger
from profile_app.models import Profile, Avatar


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя"""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )

    def update(self, instance, validated_data) -> User:
        """Обновление данных пользователя"""

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        logger.debug("User data updated")
        return instance


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара"""

    class Meta:
        model = Avatar
        fields = "src", "alt"


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя"""

    class Meta:
        model = Profile
        fields = ["fullName", "email", "phone", "avatar"]
        depth = 1

    fullName = serializers.SerializerMethodField(
        method_name="get_fullName", read_only=True
    )
    email = serializers.SerializerMethodField(method_name="get_email")
    avatar = AvatarSerializer()

    def get_fullName(self, obj) -> str:
        """Получение поля 'fullName'"""

        user: User = obj.user
        if user.first_name and user.last_name:
            return " ".join([user.first_name, user.last_name])
        elif user.first_name and not user.last_name:
            return user.first_name
        elif not user.first_name and user.last_name:
            return user.last_name
        else:
            return user.username

    def get_email(self, obj) -> str:
        """Получение поля 'email'"""

        return obj.user.email


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""

    class Meta:
        model = Profile
        fields = ["fullName", "email", "phone"]

    def update(self, instance, validated_data) -> Profile:
        """Обновление данных профиля"""

        instance.fullName = validated_data.get("fullName", instance.fullName)
        instance.email = validated_data.get("email", instance.email)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.save()
        return instance


@utils.extend_schema_serializer(
    examples=[
        utils.OpenApiExample(
            "password change example",
            value={
                "currentPassword": "oldPass123",
                "newPassword": "newPass321",
            },
        ),
    ]
)
class OldNewPasswordSerializer(serializers.Serializer):
    """Сериализатор данных для изменения пароля"""

    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)
