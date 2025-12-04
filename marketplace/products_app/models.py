from decimal import Decimal
from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from catalog_app.models import Category


class Product(models.Model):
    """Модель товара"""

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("title",)

    category = models.ForeignKey(
        Category,
        null=False,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория товара",
    )
    price = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена товара",
    )
    count = models.IntegerField(
        null=False,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Доступное количество товара",
    )
    date = models.DateTimeField(
        null=False,
        auto_now_add=True,
        verbose_name="Дата добавления товара",
    )
    title = models.CharField(
        null=False,
        max_length=100,
        verbose_name="Название товара",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Краткое описание товара",
    )
    fullDescription = models.TextField(
        null=True,
        blank=True,
        verbose_name="Полное описание товара",
    )
    freeDelivery = models.BooleanField(
        default=False,
        verbose_name="Наличие бесплатной доставки",
    )
    limited = models.BooleanField(
        default=False,
        verbose_name="Ограниченный товар",
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Доступен",
    )

    @property
    def rating(self) -> float:
        """Рейтинг товара.

        * Рассчитывается на основе оценок, указанных в 'review.rate'
        """

        product_reviews = self.reviews.all()
        rates = [review.rate for review in product_reviews]
        if not rates:
            return 0
        avg_rate = round(sum(rates) / len(rates), 1)
        return avg_rate

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Вместо удаления помечаем как недоступный"""

        self.available = False
        self.save()

    def __str__(self) -> str:
        return f"{self.title}"


def upload_product_image_to(instance: "ProductImage", filename: str) -> str:
    """Функция сохранения изображения в указанный путь"""

    return f"products/product_{instance.product.pk}/images/{filename}"


class ProductImage(models.Model):
    """Модель изображения товара"""

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    src = models.ImageField(
        upload_to=upload_product_image_to,
        verbose_name="Источник изображения",
    )
    alt = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Имя файла",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Сохранение модели"""

        self.alt = self.get_alt()
        super().save(*args, **kwargs)

    def get_alt(self) -> str:
        """Получение поля alt"""

        if not self.alt and self.src:
            self.alt = self.src.name.rsplit("/", 1)[-1]
        return self.alt or ""

    def delete(self, using: Any | None = None, keep_parents: bool = False) -> None:
        """При удалении объекта ProductImage удаляем файл изображения"""

        self.src.delete(save=True)
        super().delete(using=None, keep_parents=False)

    def __str__(self) -> str:
        return f"{self.get_alt()}"


class ProductSpecification(models.Model):
    """Модель спецификации товара"""

    class Meta:
        verbose_name = "Спецификация товара"
        verbose_name_plural = "Спецификации товаров"

    name = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Имя свойства",
    )
    value = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Значение свойства",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name="Товар",
    )

    def __str__(self) -> str:
        return f"{self.name}"


class ProductReview(models.Model):
    """Модель отзыва о товаре"""

    class Meta:
        verbose_name = "Отзыв о товаре"
        verbose_name_plural = "Отзывы о товарах"
        unique_together = ("product", "email")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар",
    )
    author = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Имя автора отзыва",
    )
    email = models.EmailField(
        null=False,
        blank=False,
        verbose_name="Email автора отзыва",
    )
    text = models.TextField(
        null=False,
        verbose_name="Текст отзыва",
    )
    rate = models.IntegerField(
        null=False,
        validators=[
            MinValueValidator(1, message="Rate must be between 1 and 5"),
            MaxValueValidator(5, message="Rate must be between 1 and 5"),
        ],
        verbose_name="Оценка товара",
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации отзыва",
    )

    def __str__(self) -> str:
        return f"Review by {self.author})"


class Sales(models.Model):
    """Модель распродаж"""

    class Meta:
        verbose_name = "Распродажа"
        verbose_name_plural = "Распродажи"

    name = models.CharField(
        max_length=200,
        verbose_name="Название распродажи",
    )
    description = models.TextField(
        null=True,
        verbose_name="Описание распродажи",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )


class SaleItems(models.Model):
    """Модель элементов распродажи"""

    class Meta:
        verbose_name = "Товар на распродаже"
        verbose_name_plural = "Товары на распродаже"
        constraints = [
            models.UniqueConstraint(fields=["product"], name="unique_product"),
            models.CheckConstraint(
                condition=models.Q(dateFrom__lt=models.F("dateTo")),
                name="check_date_constraint",
                violation_error_message="dateFrom must be less than dateTo",
            ),
        ]
        ordering = ["-discount"]

    sale = models.ForeignKey(
        "Sales",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Распродажа",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="sale_items",
        verbose_name="Товар на распродаже",
    )
    discount = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        verbose_name="Значение скидки",
    )
    dateFrom = models.DateField(verbose_name="Дата начала распродажи")
    dateTo = models.DateField(verbose_name="Дата окончания распродажи")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )

    @property
    def salePrice(self) -> Decimal:
        """Функция расчета стоимости товара с учетом скидки по распродаже"""

        sale_price = self.product.price
        date_time_now = timezone.now().date()

        if self.is_active and self.dateFrom <= date_time_now <= self.dateTo:
            sale_price -= sale_price * self.discount / 100

        return sale_price
