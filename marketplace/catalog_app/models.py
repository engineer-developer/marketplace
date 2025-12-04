from typing import Any

from django.db import models


def category_image_path(instance: "CategoryImage", filename: str) -> str:
    """Функция возвращает путь для сохранения изображения"""

    return "category/images/{filename}".format(
        filename=filename,
    )


class CategoryImage(models.Model):
    """Модель изображения категории"""

    class Meta:
        verbose_name = "Изображение категории"
        verbose_name_plural = "Изображения категорий"

    src = models.ImageField(
        upload_to=category_image_path,
        null=True,
        verbose_name="Источник изображения",
    )
    alt = models.CharField(
        null=True,
        max_length=50,
        verbose_name="Имя файла",
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

    def __str__(self) -> str:
        return f"{self.get_alt()}"


class Category(models.Model):
    """Модель категории каталога"""

    class Meta:
        ordering = ["title"]
        verbose_name = "Категория товаров"
        verbose_name_plural = "Категории товаров"

    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название категории",
    )
    image = models.OneToOneField(
        CategoryImage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="category",
        verbose_name="Изображение категории",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        related_name="subcategories",
        verbose_name="Общая категория",
    )
    favorite = models.BooleanField(
        default=False,
        verbose_name="В избранных",
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Доступна",
    )

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Вместо удаления помечаем как недоступный"""

        self.available = False
        self.save()

    def __str__(self) -> str:
        return f"{self.title}"
