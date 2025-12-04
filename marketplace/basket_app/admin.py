from django.contrib import admin
from django.contrib.sessions.models import Session
from django.db.models import QuerySet
from django.db.models.query_utils import Q
from django.http import HttpRequest
from django.utils import timezone

from basket_app.models import Basket, BasketItem
from mainsite.main_logger import logger


@admin.action(
    description="Удалить корзины анонимов с истекшим сроком действия сессии "
    "или не присоединенные к активным сессиям",
)
def delete_anonim_basket_with_expired_sessions(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
):
    expired_sessions_keys = Session.objects.filter(
        expire_date__lt=timezone.now()
    ).values_list("session_key", flat=True)
    logger.debug("expired sessions keys: %s", expired_sessions_keys)

    not_expired_keys = Session.objects.filter(
        expire_date__gt=timezone.now()
    ).values_list("session_key", flat=True)
    logger.debug("not expired sessions keys: %s", not_expired_keys)

    baskets = queryset.filter(user=None).filter(
        Q(session_key__in=expired_sessions_keys) | ~Q(session_key__in=not_expired_keys)
    )
    logger.debug("basket with expired sessions: %s", baskets)
    modeladmin.message_user(
        request,
        message="Удалено {} корзин".format(baskets.count()),
    )
    baskets.delete()


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 0
    show_change_link = True


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """Админка корзины"""

    list_display = (
        "id",
        "user_name",
        "session_key",
        "created_at",
        "updated_at",
        "total_price",
        "total_quantity",
    )
    list_display_links = (
        "id",
        "user_name",
        "session_key",
    )
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (BasketItemInline,)
    actions = [
        delete_anonim_basket_with_expired_sessions,
    ]

    def user_name(self, obj):
        """Получение имени пользователя"""

        if not obj.user:
            return "anonim"
        return obj.user.username


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    """Админка элементов корзины"""

    list_display = (
        "id",
        "basket_name",
        "product",
        "quantity",
        "added_at",
        "total_price",
    )
    list_display_links = (
        "basket_name",
        "product",
    )
    list_filter = (
        "added_at",
        "basket",
    )
    ordering = ("-added_at",)

    def basket_name(self, obj):
        """Получение basket_name"""

        if len(obj.basket.__str__()) > 40:
            return obj.basket.__str__()[:35] + "..."
        return obj.basket.__str__()
