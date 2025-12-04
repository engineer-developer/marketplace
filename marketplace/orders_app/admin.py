from django.contrib import admin

from orders_app.models import Order, OrderProduct, Payment, Delivery


class OrderProductInline(admin.TabularInline):
    """Inline для модели товара в заказе"""

    model = OrderProduct
    verbose_name = "Товары в заказе"
    verbose_name_plural = "Товары в заказе"
    extra = 0
    fields = ["product", "count", "price"]
    readonly_fields = ["product", "count", "price"]
    can_delete = False


class PaymentInline(admin.StackedInline):
    """Inline для модели оплаты"""

    model = Payment
    verbose_name = "Сведения об оплате"
    extra = 0
    readonly_fields = ["number", "name", "month", "year", "code", "created_at"]
    can_delete = False
    fieldsets = [
        (
            "Осторожно - конфиденциальные данные!",
            {
                "fields": ("number", "name", "month", "year", "code", "created_at"),
                "classes": ("collapse",),
            },
        )
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка заказов"""

    list_display = (
        "id",
        "order_name",
        "user",
        "createdAt",
        "status",
    )
    list_display_links = ("order_name",)
    readonly_fields = (
        "status",
        "totalCost",
        "createdAt",
        "user_name",
        "user_full_name",
        "user_email",
        "user_phone",
    )
    inlines = (
        OrderProductInline,
        PaymentInline,
    )
    fieldsets = (
        (
            None,
            {"fields": ("status", "totalCost", "createdAt")},
        ),
        (
            "Заказчик товара",
            {
                "fields": (
                    "user_name",
                    "user_full_name",
                    "user_email",
                    "user_phone",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Получатель товара",
            {
                "fields": ("fullName", "email", "phone"),
                "classes": ("collapse",),
            },
        ),
        (
            "Сведения о доставке",
            {
                "fields": ("deliveryType", "paymentType", "city", "address"),
                "classes": ("collapse",),
            },
        ),
    )

    def order_name(self, obj):
        """Получаем 'order_name'"""
        return obj.__str__()

    order_name.short_description = "Название заказа"

    def user_name(self, obj):
        """Получаем 'user_name'"""
        return obj.user.username

    user_name.short_description = "Имя пользователя"

    def user_full_name(self, obj):
        """Получаем 'user_full_name'"""
        first_name = obj.user.first_name if obj.user.first_name else ""
        last_name = obj.user.last_name if obj.user.last_name else ""
        full_name = first_name + " " + last_name
        return full_name

    user_full_name.short_description = "Полное имя пользователя"

    def user_email(self, obj):
        """Получаем 'user_email'"""
        return obj.user.email if obj.user.email else "-"

    user_email.short_description = "Email пользователя"

    def user_phone(self, obj):
        """Получаем 'user_phone'"""
        return obj.user.profile.phone if obj.user.profile.phone else "-"

    user_phone.short_description = "Телефон пользователя"

    def get_queryset(self, request):
        """
        Если пользователь не состоит в группах "admins" и "seller_assistants",
        то в админке выводятся заказы принадлежащие пользователю
        """
        user = request.user
        qs = super().get_queryset(request)
        if user.groups.filter(name__in=["admins", "seller_assistants"]):
            return qs
        return qs.filter(user=request.user)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """Админка доставки"""

    list_display = (
        "ordinary_price",
        "express_price",
        "free_delivery_price",
    )
    list_display_links = (
        "ordinary_price",
        "express_price",
        "free_delivery_price",
    )

    def has_module_permission(self, request):
        if request.user.groups.filter(name="buyers").exists():
            return False
        return super().has_module_permission(request)

    def has_add_permission(self, request):
        """Разрешаем добавление только если объект доставки еще не существует"""

        return not Delivery.objects.exists()

    def has_change_permission(self, request, obj=None):
        """Разрешаем редактирование только существующего объекта доставки"""

        return Delivery.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удалять объект доставки"""

        return False

    # def get_actions(self, request):
    #     """Запрещаем удалять объект доставки через action"""
    #
    #     actions = super().get_actions(request)
    #     if "delete_selected" in actions:
    #         del actions["delete_selected"]
    #     return actions

    @admin.register(Payment)
    class PaymentAdmin(admin.ModelAdmin):
        """Админка платежей"""

        list_display = ("id", "created_at", "order")
        list_display_links = ("id", "created_at", "order")
        fields = ("created_at", "order")
        readonly_fields = ("created_at", "order")
