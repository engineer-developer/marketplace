from django.contrib.auth.models import User
from django.http.response import Http404
from django.shortcuts import get_object_or_404

from mainsite.handle_errors import handle_serializer_not_valid
from mainsite.main_logger import logger
from products_app.models import Product
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request

from basket_app.models import Basket
from basket_app.serializers import (
    BasketItemSerializer,
    ProductAddOrDeleteSerializer,
)


def get_or_create_basket(request: Request) -> Basket:
    """Получение или создание корзины"""

    user: User = request.user
    if user.is_authenticated:
        basket, created = Basket.objects.get_or_create(user=user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        basket, create = Basket.objects.get_or_create(
            user=None,
            session_key=session_key,
        )
    return basket


def get_product_and_product_quantity(
    request: Request,
) -> tuple[Product, int] | Response:
    """Получение объекта товара и его количества из запроса"""

    serializer = ProductAddOrDeleteSerializer(data=request.data)
    if not serializer.is_valid():
        return handle_serializer_not_valid(serializer)

    logger.debug("Payload is valid")

    validated_payload: dict = serializer.validated_data
    product_id: int = int(validated_payload["id"])
    product_quantity: int = int(validated_payload["count"])

    try:
        product: Product = get_object_or_404(Product, id=product_id)
        logger.debug("Product: %s", product)
    except Http404 as exc:
        logger.error("Product %s not found", product_id)
        return Response(exc.args[0], status=status.HTTP_404_NOT_FOUND)

    return product, product_quantity


def get_products_data_from_basket(basket: Basket) -> list[dict]:
    """Получение списка данных о товарах в корзине"""

    basket_items = basket.items
    serializer = BasketItemSerializer(basket_items, many=True)
    products: list[dict] = [item["product"] for item in serializer.data]
    return products
