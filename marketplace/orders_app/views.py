from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular import utils
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from mainsite.main_logger import logger
from orders_app.handle_cases import handle_already_paided
from mainsite.handle_errors import handle_serializer_not_valid
from orders_app.models import Order, OrderProduct
from orders_app.serializers import (
    ItemsFromBasketSerializer,
    OrderDeliveryInfoSerializer,
    OrderSerializer,
    PaymentSerializer,
    PaymentPayloadSerializer,
)
from orders_app.utils import (
    update_order_with_user_data,
    update_order_total_cost_with_product_cost,
    get_order_by_id,
    update_order_total_cost_with_delivery_price,
)
from products_app.models import Product


class OrdersListCreateApiView(generics.ListCreateAPIView):
    """Представление для получения списка заказов или создания заказа"""

    queryset = Order.objects.prefetch_related(
        "user",
        "products",
        "products__product",
        "products__product__category",
        "products__product__tags",
        "products__product__images",
        "products__product__reviews",
    )
    serializer_class = OrderSerializer
    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()

    @utils.extend_schema(
        tags=["order"],
        description="Get orders",
        summary="Get orders",
        responses=(
            {
                200: utils.OpenApiResponse(
                    response=OrderSerializer(many=True),
                    description="successful operation",
                )
            }
        ),
    )
    def get(self, request, *args, **kwargs) -> Response[list[dict]]:
        """Получение списка заказов пользователя"""

        queryset = self.get_queryset().filter(available=True).filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @utils.extend_schema(
        tags=["order"],
        description="Create order",
        summary="Create order",
        request=ItemsFromBasketSerializer(many=True),
        responses=(
            {
                201: utils.OpenApiResponse(
                    description="Order created successfully.",
                )
            }
        ),
    )
    def post(self, request, *args, **kwargs) -> Response:
        """Создание нового заказа"""

        order = Order.objects.create(status="NEW")
        order.totalCost = 0
        order.save()

        serializer = ItemsFromBasketSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return handle_serializer_not_valid(serializer)

        logger.debug("Items from basket: %s", serializer.validated_data)

        for item in serializer.validated_data:
            product_id = item["id"]
            products_count = item["count"]
            products_total_price = item["price"]

            product = Product.objects.get(id=product_id)
            order_product, op_created = OrderProduct.objects.get_or_create(
                order=order,
                product=product,
            )
            order_product.count = products_count
            order_product.price = products_total_price
            order_product.save()

        logger.debug("Order №%s created. Need to specify the order details", order.id)

        return Response(data={"orderId": order.id}, status=status.HTTP_201_CREATED)


class OrderDetailsApiView(generics.RetrieveUpdateAPIView):
    """Представление для получения или подтверждения заказа по его 'id"""

    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        elif self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()

    @utils.extend_schema(
        tags=["order"],
        description="Get order details",
        summary="Get order details",
        parameters=[
            utils.OpenApiParameter(
                description="order id",
                name="id",
                type=utils.OpenApiTypes(utils.OpenApiTypes.INT),
                location=utils.OpenApiParameter.PATH,
                required=True,
            ),
        ],
        responses=(
            {
                200: utils.OpenApiResponse(
                    description="successful operation",
                    response=OrderSerializer,
                )
            }
        ),
    )
    def get(self, request, *args, id=None, **kwargs):
        """Получение заказа по его 'id"""

        user: User = request.user
        order: Order = get_order_by_id(order_id=id)

        if isinstance(order, Order) and order.user is None and user.is_authenticated:
            order = update_order_with_user_data(order, user)

        if order.totalCost == 0:
            order = update_order_total_cost_with_product_cost(order)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @utils.extend_schema(
        tags=["order"],
        description="Confirm order",
        summary="Confirm order",
        parameters=[
            utils.OpenApiParameter(
                description="order id",
                name="id",
                type=utils.OpenApiTypes(utils.OpenApiTypes.INT),
                location=utils.OpenApiParameter.PATH,
                required=True,
            ),
        ],
        request=OrderDeliveryInfoSerializer,
        responses=(
            {
                202: utils.OpenApiResponse(
                    response=OrderSerializer,
                    description="successful operation",
                )
            }
        ),
    )
    def post(self, request, *args, id=None, **kwargs):
        """Подтверждение заказа"""

        # Получаем заказ по его id
        order: Order = get_order_by_id(order_id=id)

        # Если заказ уже оплачен, завершаем подтверждение заказа
        if order.is_paided:
            return handle_already_paided(order)

        # Валидируем переданные в запросе сведения о доставке товара
        serializer = OrderDeliveryInfoSerializer(
            order,
            data=request.data,
        )

        # Если валидация не удалась, завершаем подтверждение заказа
        if not serializer.is_valid():
            return handle_serializer_not_valid(serializer)

        # Обновляем данные заказа сведениями о доставке
        order = serializer.save()

        # Обновляем итоговую стоимость заказа с учетом способа доставки
        order = update_order_total_cost_with_delivery_price(order)

        # Устанавливаем статус заказа в 'confirmed'
        order.status = Order.OrderStatusChoices.CONFIRMED
        order.save()
        logger.debug("Order №%s confirmed", order.id)

        # Получаем пользователя из заказа
        user = order.user

        # Выполняем очистку корзины пользователя
        if hasattr(user, "basket"):
            user.basket.flush()
            logger.debug("Basket is flushed")

        # Возвращаем значение 'orderId', ожидаемое фронтом для оплаты заказа
        return Response(
            data={"orderId": order.id},
            status=status.HTTP_202_ACCEPTED,
        )


class PaymentApiView(generics.CreateAPIView):
    """Представление для выполнения оплаты"""

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    @utils.extend_schema(
        tags=["payment"],
        summary="Payment",
        description="Payment",
        parameters=[
            utils.OpenApiParameter(
                name="id",
                location=utils.OpenApiParameter.PATH,
                type=utils.OpenApiTypes.INT,
                required=True,
                description="order id",
            )
        ],
        request=PaymentPayloadSerializer,
        responses={
            201: utils.OpenApiResponse(
                response=dict,
                description="successful operation",
                examples=[
                    utils.OpenApiExample(name="paymentId", value={"paymentId": 1})
                ],
            )
        },
    )
    def post(self, request, *args, id=None, **kwargs):
        """Выполнение оплаты"""

        # Получаем объект заказа
        order = get_order_by_id(order_id=id)
        order.status = Order.OrderStatusChoices.AWAITING_PAYMENT
        order.save()
        logger.debug("Order %s awaiting payment...", order.id)

        # Получаем данные об оплате из запроса
        payload = request.data

        try:
            # Получаем объект оплаты из заказа
            payment = order.payment
            # Обновляем объект 'payment' новыми данными из 'payload'
            serializer = PaymentSerializer(payment, data=payload)

        except ObjectDoesNotExist:
            # Попадаем в исключение если у заказа еще нет оплаты

            # Добавляем в 'payload' информацию о заказе
            payload.update({"order": order.id})
            # Создаём объект сериализатора с обновленным 'payload'
            serializer = PaymentSerializer(data=payload)

        # Валидируем данные, переданные в сериализатор
        if not serializer.is_valid():
            order.status = Order.OrderStatusChoices.PAYMENT_ERROR
            order.save()
            return handle_serializer_not_valid(serializer)

        logger.debug("Payment data is valid")

        # Сохраняем объект оплаты в базу данных
        payment = serializer.save()

        order.status = Order.OrderStatusChoices.PAIDED
        order.save()
        logger.debug("Order %s was paided", order.id)

        return Response(
            data={"paymentId": payment.id},
            status=status.HTTP_200_OK,
        )
