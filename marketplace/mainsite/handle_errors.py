from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from mainsite.main_logger import logger


def handle_serializer_not_valid(serializer: Serializer) -> Response:
    """Логируем ошибку и возвращаем ответ"""

    logger.error(
        "Serializer validation error: %s",
        serializer.errors,
    )
    return Response(
        data=serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )
