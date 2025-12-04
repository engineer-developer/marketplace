from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.db import models

from products_app.models import Product


class Order(models.Model):
    """Модель заказа"""

    class OrderChoices(models.TextChoices):
        """Базовый класс для классов выбора"""

        @classmethod
        def get_value_by_label(cls, label: str) -> str | None:
            """
            Возвращает значение 'value' (первый элемент кортежа) на основе
            переданного в функцию значения метки 'label' (второй элемент
            кортежа, который представляет собой строковое удобочитаемое
            значение)
            """
            for choice in cls:
                if choice.label == label:
                    return choice.value
            return None

    class OrderStatusChoices(OrderChoices):
        """Выбор статуса заказа"""

        NEW = ("NEW", "new")
        CONFIRMED = ("CONFIRMED", "confirmed")
        AWAITING_PAYMENT = ("AWAITING_PAYMENT", "awaiting_payment")
        PAYMENT_ERROR = ("PAYMENT_ERROR", "payment_error")
        PAIDED = ("PAIDED", "paided")

    class OrderDeliveryTypeChoices(OrderChoices):
        """Выбор способа доставки заказа"""

        ORDINARY = ("ORDINARY", "ordinary")
        EXPRESS = ("EXPRESS", "express")

    class OrderPaymentTypeChoices(OrderChoices):
        """Выбор способа оплаты заказа"""

        ONLINE = ("ONLINE", "online")
        SOMEONE = ("SOMEONE", "someone")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-createdAt"]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
        verbose_name="Пользователь",
    )
    createdAt = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    fullName = models.CharField(
        max_length=120,
        null=True,
        verbose_name="Полное имя получателя",
    )
    email = models.EmailField(
        max_length=120,
        null=True,
        verbose_name="Email получателя",
    )
    phone = models.CharField(
        max_length=11,
        null=True,
        verbose_name="Телефон получателя",
    )
    deliveryType = models.CharField(
        choices=OrderDeliveryTypeChoices.choices,
        default=OrderDeliveryTypeChoices.ORDINARY,
        max_length=100,
        null=True,
        verbose_name="Способ доставки",
    )
    paymentType = models.CharField(
        choices=OrderPaymentTypeChoices.choices,
        default=OrderPaymentTypeChoices.ONLINE,
        max_length=100,
        null=True,
        verbose_name="Способ оплаты",
    )
    totalCost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Итоговая стоимость заказа",
    )
    status = models.CharField(
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.NEW,
        max_length=100,
        null=True,
        verbose_name="Статус заказа",
    )
    city = models.CharField(
        max_length=120,
        null=True,
        verbose_name="Город доставки",
    )
    address = models.CharField(
        max_length=120,
        null=True,
        verbose_name="Адрес доставки",
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Доступен",
    )

    @property
    def is_paided(self) -> bool:
        """Свойство проверяющее оплачен ли заказ"""
        return self.status == Order.OrderStatusChoices.PAIDED

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Вместо удаления помечаем как недоступный"""

        self.available = False
        self.save()

    def __str__(self) -> str:
        return f"Заказ № {self.id}"


class OrderProduct(models.Model):
    """Модель сведений о товаре в заказе"""

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"
        unique_together = (("order", "product"),)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="orderProduct",
        verbose_name="Товар в заказе",
    )
    count = models.PositiveIntegerField(
        default=1,
        null=True,
        verbose_name="Количество товара в заказе",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name="Общая цена на момент покупки",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления",
    )

    def __str__(self) -> str:
        return f"{self.count} x {self.product.title} в заказе"


class Payment(models.Model):
    """Модель оплаты"""

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    number = models.CharField(
        max_length=8,
        null=True,
        verbose_name="Номер карты",
    )
    name = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Имя владельца карты",
    )
    month = models.CharField(
        max_length=2,
        null=True,
        verbose_name="Месяц выпуска карты",
    )
    year = models.CharField(
        max_length=4,
        null=True,
        verbose_name="Год выпуска карты",
    )
    code = models.CharField(
        max_length=3,
        null=True,
        verbose_name="Код карты",
    )

    order = models.OneToOneField(
        Order,
        related_name="payment",
        on_delete=models.PROTECT,
        null=True,
        verbose_name="Заказ",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оплаты",
    )

    def __str__(self) -> str:
        if self.order:
            return f"Оплата заказа №{self.order.pk}"
        return "Оплата заказа"


class Delivery(models.Model):
    """Модель доставки"""

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставка"

    ordinary_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=200,
        verbose_name="Стоимость обычной доставки",
    )
    express_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500,
        verbose_name="Стоимость экспресс доставки",
    )
    free_delivery_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2000,
        verbose_name="Стоимость заказа для бесплатной доставки",
    )
