from typing import Any

from django.contrib.auth.models import User
from django.db import models

from mainsite.settings import MEDIA_ROOT


class Profile(models.Model):
    """Модель профиля пользователя"""

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
            models.UniqueConstraint(fields=["phone"], name="unique_phone"),
        ]

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="profile",
        verbose_name="Пользователь",
    )
    fullName = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Полное имя пользователя",
    )
    email = models.EmailField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Email пользователя",
    )
    phone = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        verbose_name="Телефон пользователя",
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Доступен",
    )

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Вместо удаления помечаем как недоступный"""

        self.available = False
        self.user.is_active = False
        self.save()

    def __str__(self) -> str:
        return f"'Profile {self.id}'"


def upload_avatar(instance: "Avatar", filename: str) -> str:
    """Путь для сохранения изображения аватара"""

    if instance.profile:
        return "users/user_{}/profile/avatar/{}".format(
            instance.profile.user.pk,
            filename,
        )
    else:
        return "users/profile/avatars/{}".format(filename)


class Avatar(models.Model):
    """Модель аватара пользователя"""

    class Meta:
        verbose_name = "Аватар пользователя"
        verbose_name_plural = "Аватары пользователей"

    profile = models.OneToOneField(
        "Profile",
        on_delete=models.CASCADE,
        related_name="avatar",
        null=True,
        verbose_name="Профиль пользователя",
    )
    src = models.ImageField(
        upload_to=upload_avatar,
        null=True,
        verbose_name="Источник изображения",
    )
    alt = models.CharField(
        max_length=50,
        null=True,
        verbose_name="Имя файла",
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Сохранение аватара"""

        self.alt = self.get_alt()
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Удаление аватара"""

        file = MEDIA_ROOT / self.src.path
        file.unlink(missing_ok=True)
        super().delete(*args, **kwargs)

    def get_alt(self) -> str:
        """Получение поля alt"""

        if not self.alt and self.src:
            self.alt = self.src.name.rsplit("/", 1)[-1]
        return self.alt or ""

    def __str__(self) -> str:
        return f"{self.get_alt()}"
