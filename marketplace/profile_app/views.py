from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from mainsite.handle_errors import handle_serializer_not_valid
from mainsite.main_logger import logger
from profile_app.forms import ImageUploadForm
from profile_app.models import Avatar, Profile
from profile_app.utils import (
    update_user_profile,
    update_user_data_with_profile,
)
from profile_app.serializers import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    AvatarSerializer,
    OldNewPasswordSerializer,
)


class AvatarAPIView(views.APIView):
    """Представление аватара пользователя"""

    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["profile"],
        summary="Update user avatar",
        description="update user avatar",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "avatar": {
                        "type": "string",
                        "format": "binary",
                        "description": "Загружаемый файл",
                    },
                },
            }
        },
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="successful operation")
        },
    )
    def post(self, request):
        """Создает или обновляет аватар пользователя"""

        file_max_size = 2 * 1024 * 1024

        form = ImageUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return Response(form.errors, status=400)

        image = form.cleaned_data["avatar"]

        if image.size > file_max_size:
            return Response("File too large", status=400)

        profile, profile_created = Profile.objects.get_or_create(user=request.user)

        if profile_created:
            avatar = Avatar.objects.create(
                profile=profile,
                src=image,
            )
        else:
            avatar, avatar_created = Avatar.objects.get_or_create(profile=profile)
            if not avatar_created:
                avatar.src.delete()
            avatar.src = image
            avatar.save()

        logger.debug("Avatar src: %s ", avatar.src)

        return Response(
            data={"avatar": avatar.src.path},
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(views.APIView):
    """Представление профиля пользователя"""

    serializer_class = ProfileSerializer

    # Доступ только для авторизованных пользователей
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["profile"],
        summary="Get user profile",
        description="Get user profile",
        responses={
            200: OpenApiResponse(
                description="successful operation",
                response=ProfileSerializer,
            )
        },
    )
    def get(self, request):
        """Получает данные профиля пользователя"""

        try:
            profile = get_object_or_404(Profile, user=request.user)
        except Http404:
            return Response(
                "User profile not found",
                status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfileSerializer(profile)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["profile"],
        summary="Update user info",
        description="update user info",
        request=ProfileUpdateSerializer,
        responses={
            "200": OpenApiResponse(
                description="successful operation",
                response=ProfileSerializer,
            )
        },
    )
    def post(self, request):
        """Обновляет данные профиля пользователя"""

        user = request.user
        try:
            profile = get_object_or_404(Profile, user=user)
        except Http404 as exc:
            logger.error("Order %s not found", id)
            return Response(data=str(exc), status=404)

        profile = update_user_profile(profile=profile, data=request.data)
        update_user_data_with_profile(user=user)

        serializer = ProfileSerializer(profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UpdateUserPasswordAPIView(generics.GenericAPIView):
    """Представление для смены пароля пользователя"""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["profile"],
        summary="Update user password",
        description="update user password",
        request=OldNewPasswordSerializer,
        responses={"202": OpenApiResponse(description="user password updated")},
    )
    def post(self, request):
        """Обновляет пароль пользователя"""

        user: User = request.user
        serializer = OldNewPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return handle_serializer_not_valid(serializer)

        current_password = serializer.validated_data.get("currentPassword")
        new_password = serializer.validated_data.get("newPassword")

        if not user.check_password(current_password):
            return Response(data="Current password is incorrect", status=400)

        user.set_password(new_password)
        user.save()
        login(request, user)

        return Response(data="successful operation", status=status.HTTP_202_ACCEPTED)
