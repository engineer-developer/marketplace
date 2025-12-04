from django.contrib.auth.models import User
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from mainsite.main_logger import logger
from orders_app.models import Order, Delivery


def get_order_by_id(order_id: int) -> Order | Response:
    """Получаем заказ по его 'id'"""

    if not order_id:
        error_message = "Must specify 'order_id'"
        logger.error("%s", error_message)
        data = {"input_error": error_message}
        return Response(data=data, status=404)

    try:
        order = get_object_or_404(Order, id=order_id)
        logger.debug("Get order №%s", order.id)
        return order
    except Http404 as exc:
        logger.error("Order %s not found", id)
        return Response(data=str(exc), status=404)


def update_order_with_user_data(order: Order, user: User) -> Order:
    """Обновляем заказ данными пользователя"""

    order.user = user
    order.fullName = user.profile.fullName
    order.email = user.email
    order.phone = user.profile.phone
    order.save()
    return order


def update_order_total_cost_with_product_cost(order: Order) -> Order:
    """Обновляем итоговую стоимость заказа с учетом стоимости товаров в заказе"""

    total_price = 0
    for product in order.products.all():
        total_price += product.price * product.count
    order.totalCost = total_price
    order.save()
    return order


def update_order_total_cost_with_delivery_price(order: Order) -> Order:
    """Обновляем итоговую стоимость заказа с учетом стоимости доставки"""

    delivery = Delivery.objects.first()

    # Если стоимость заказа больше 'free_delivery_price', то доставка бесплатная
    if order.totalCost > delivery.free_delivery_price:
        total_cost = order.totalCost
    # в противном случае добавляем к стоимости заказа стоимость обычной доставки
    else:
        total_cost = order.totalCost + delivery.ordinary_price

    # Если выбрана экспресс доставка, то доплачиваем за неё
    if order.deliveryType == Order.OrderDeliveryTypeChoices.EXPRESS.value:
        total_cost += delivery.express_price

    # Присваиваем итоговую стоимость заказу
    order.totalCost = total_cost
    order.save()
    return order
