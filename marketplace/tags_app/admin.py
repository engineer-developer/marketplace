from django.contrib import admin

from products_app.models import Product
from tags_app.models import Tag


class ProductsInline(admin.TabularInline):
    """Inline для модели товара, имеющего связь M2M с моделью метки"""

    model = Product.tags.through
    extra = 0
    verbose_name_plural = "Товары"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка метки"""

    list_display = (
        "id",
        "name",
    )
    list_display_links = ("name",)
    ordering = ("name",)
    inlines = (ProductsInline,)
