from rest_framework.response import Response
from rest_framework import status

from mainsite.main_logger import logger
from orders_app.models import Order


def handle_already_paided(order: Order) -> Response:
    """Логируем ошибку и возвращаем ответ"""

    logger.error(
        "Order %s already paided",
        order.id,
    )
    return Response(
        f"Order {order.id} already paided",
        status=status.HTTP_406_NOT_ACCEPTABLE,
    )
