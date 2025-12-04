import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from auth_app.serializers import (
    SignInCredentialsSerializer,
    SignUpCredentialsSerializer,
)
from auth_app.utils import create_user
from mainsite.handle_errors import handle_serializer_not_valid
from profile_app.utils import create_user_profile


class SignInView(APIView):
    """Вход пользователя на сайт"""

    serializer_class = SignInCredentialsSerializer

    @extend_schema(
        summary="Sign in",
        description="sign in",
        tags=["auth"],
        parameters=[SignInCredentialsSerializer],
        responses={
            200: OpenApiResponse(
                description="successful operation",
                response=None,
            ),
            500: OpenApiResponse(
                description="unsuccessful operation",
                response=None,
            ),
        },
    )
    def post(self, request: Request):
        """Проверка регистрационных данных и аутентификация пользователя"""

        request_body = json.loads(request.body)
        serializer = SignInCredentialsSerializer(data=request_body)

        if not serializer.is_valid():
            return handle_serializer_not_valid(serializer)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(
            request=request,
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                "Authenticate error",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response(
            "Successfully sign-in",
            status=status.HTTP_200_OK,
        )


class SignOutView(APIView):
    """Выход пользователя с сайта"""

    serializer_class = None

    @extend_schema(
        summary="Sign out",
        description="sign out",
        tags=["auth"],
        responses={
            200: OpenApiResponse(
                description="successful operation",
                response=None,
            ),
        },
    )
    def post(self, request: Request):
        """Выход из системы"""

        logout(request)
        return redirect("/")


class RegistrationView(APIView):
    """Регистрация нового пользователя"""

    serializer_class = SignUpCredentialsSerializer

    @extend_schema(
        summary="Sign up",
        description="sign up",
        tags=["auth"],
        parameters=[SignUpCredentialsSerializer],
        responses={
            200: OpenApiResponse(
                description="successful operation",
                response=None,
            ),
            500: OpenApiResponse(
                description="unsuccessful operation",
                response=None,
            ),
        },
    )
    def post(self, request: Request):
        """Проверка регистрационных данных, создание пользователя и его вход в систему"""

        # Получаем переданные в запросе данные
        payload = json.loads(request.body)

        # Создаем десериализатор данных
        serializer = SignUpCredentialsSerializer(data=payload)

        if not serializer.is_valid():
            return handle_serializer_not_valid(serializer)

        # Создаем нового пользователя
        user = create_user(data=serializer.validated_data)

        # Создаем профиль для нового пользователя
        if user and isinstance(user, User):
            create_user_profile(user=user)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Логинимся под именем нового пользователя
        login(request=request, user=user)
        return Response(
            "User registration successful",
            status=status.HTTP_200_OK,
        )
