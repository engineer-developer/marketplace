from django.http.response import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from basket_app.models import Basket, BasketItem
from basket_app.serializers import (
    ProductAddOrDeleteSerializer,
)
from basket_app.utils import (
    get_or_create_basket,
    get_product_and_product_quantity,
    get_products_data_from_basket,
)
from mainsite.main_logger import logger
from products_app.serializers import ProductShortSerializer


class BasketAPIView(APIView):
    """Представление корзины"""

    http_method_names = ["get", "post", "delete"]

    @extend_schema(
        tags=["basket"],
        summary="Get items from basket",
        description="Get items from basket",
        responses={
            200: OpenApiResponse(
                description="successful operation",
                response=ProductShortSerializer(many=True),
            )
        },
    )
    def get(
        self, request: Request, *args, **kwargs
    ) -> Response[list[ProductShortSerializer]]:
        """Получение сведений о товарах в корзине"""

        basket = get_or_create_basket(request)
        products_data: list[dict] = get_products_data_from_basket(basket)
        logger.debug("Count product items in basket: %s", len(products_data))
        return Response(products_data, 200)

    @extend_schema(
        tags=["basket"],
        summary="Add item to basket",
        description="Add item to basket",
        request=ProductAddOrDeleteSerializer,
        responses={
            200: OpenApiResponse(
                description="successful operation",
                response=ProductShortSerializer(many=True),
            )
        },
    )
    def post(
        self, request: Request, *args, **kwargs
    ) -> Response[list[ProductShortSerializer]]:
        """Добавление товара в корзину"""

        basket: Basket = get_or_create_basket(request)
        product, product_quantity = get_product_and_product_quantity(request)

        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket,
            product=product,
        )
        if created:
            basket_item.quantity = product_quantity
        else:
            basket_item.quantity += product_quantity
        basket_item.save()
        basket.save(update_fields=["updated_at"])
        logger.debug(
            "added %s product%s '%s' to basket",
            product_quantity,
            "s" if product_quantity > 1 else "",
            product,
        )

        products_data: list[dict] = get_products_data_from_basket(basket)
        return Response(products_data, 200)

    @extend_schema(
        tags=["basket"],
        summary="Remove item from basket",
        description="Remove item from basket",
        request=ProductAddOrDeleteSerializer,
        responses={
            200: OpenApiResponse(
                description="successful operation",
                response=list[str],
            )
        },
    )
    def delete(self, request: Request, *args, **kwargs) -> Response[list[str]]:
        """Удаление товара из корзины"""

        basket: Basket = get_or_create_basket(request)
        product, product_quantity = get_product_and_product_quantity(request)

        try:
            basket_item = get_object_or_404(BasketItem, basket=basket, product=product)
            logger.debug("basket item: %s", basket_item)
        except Http404 as exc:
            logger.error("basket item not found")
            return Response(exc.args[0], status=404)

        if basket_item.quantity <= product_quantity:
            basket_item.delete()
            logger.debug("deleted product '%s' from basket", product)
            return Response(data=["product deleted"], status=200)
        else:
            basket_item.quantity -= product_quantity
            basket_item.save()
            logger.debug(
                "deleted %s product%s '%s' from basket",
                product_quantity,
                "s" if product_quantity > 1 else "",
                product,
            )

            products_data: list[dict] = get_products_data_from_basket(basket)
            return Response(products_data, 200)
