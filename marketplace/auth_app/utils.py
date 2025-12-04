from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status

from mainsite.main_logger import logger


def create_user(data: dict) -> User | Response:
    """Создание пользователя с использованием переданных данных"""

    name = data["name"]
    if name and isinstance(name, str):
        name = name.strip()

    username = data["username"]
    if username and isinstance(username, str):
        username = username.strip()

    password = data["password"]
    if password and isinstance(password, str):
        password = password.strip()

    first_name, last_name = None, None

    if isinstance(name, str) and " " in name:
        first_name, last_name = name.split(" ", 1)

    try:
        user = User.objects.create(
            first_name=first_name if first_name else name,
            last_name=last_name if last_name else "",
            username=username,
            password=make_password(password),
        )
        logger.debug("Created user: %s", user)

    except IntegrityError as exc:
        logger.error("Integrity error: %s", str(exc))
        return Response(
            f"User with username '{username}' already exists",
            status=status.HTTP_409_CONFLICT,
        )

    return user
