from rest_framework import serializers


class SignInCredentialsSerializer(serializers.Serializer):
    """Сериализатор данных для входа в систему"""

    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)


class SignUpCredentialsSerializer(SignInCredentialsSerializer):
    """Сериализатор регистрационных данных"""

    name = serializers.CharField(required=True, allow_blank=False)
