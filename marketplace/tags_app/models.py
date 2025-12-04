from django.db import models


class Tag(models.Model):
    """Модель метки"""

    class Meta:
        ordering = ("name",)
        verbose_name = "Метка"
        verbose_name_plural = "Метки"

    name = models.CharField(
        max_length=50,
        verbose_name="Название метки",
    )
    products = models.ManyToManyField(
        "products_app.Product",
        related_name="tags",
        verbose_name="Товар",
    )

    def __str__(self) -> str:
        return self.name
