from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models

from products_app.models import Product


class Basket(models.Model):
    """Модель корзины"""

    class Meta:
        verbose_name = "Корзина пользователя"
        verbose_name_plural = "Корзины пользователей"
        unique_together = [["user", "session_key"]]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="basket",
        verbose_name="Пользователь",
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Ключ сессии",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    @property
    def total_price(self) -> Decimal:
        """Стоимость всей корзины"""
        prices_list = [item.total_price for item in self.items.all()]
        return sum(prices_list, Decimal("0.00"))

    @property
    def total_quantity(self) -> int:
        """Количество товаров в корзине"""
        return sum([item.quantity for item in self.items.all()])

    def flush(self) -> None:
        """Очистка корзины"""
        for item in self.items.all():
            item.delete()

    def __str__(self) -> str:
        if self.user:
            return f"Корзина '{self.user}' (pk: {self.pk})"
        return f"Корзина анонима (pk: {self.pk})"


class BasketItem(models.Model):
    """Модель элементов корзины"""

    class Meta:
        verbose_name = "Товары в корзине"
        verbose_name_plural = "Товары в корзинах"

    basket = models.ForeignKey(
        Basket,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="basket_item",
        verbose_name="Товар в корзине",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество товара в корзине",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления",
    )

    @property
    def total_price(self) -> Decimal:
        """Полная стоимость корзины учетом стоимости и количества товаров"""
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.title} in {self.basket}"
