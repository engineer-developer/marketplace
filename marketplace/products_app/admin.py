from django import forms
from django.contrib import admin
from django.contrib.admin.decorators import action
from django.db import models
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.urls.conf import path


from products_app.models import (
    Product,
    ProductImage,
    ProductReview,
    ProductSpecification,
    Sales,
    SaleItems,
)
from products_app.forms import ProductAddForm, ProductImageForm
from catalog_app.models import Category


class ProductImageInline(admin.TabularInline):
    """Inline для модели изображения товара"""

    model = ProductImage
    extra = 0
    verbose_name = "Image"
    verbose_name_plural = "Images"
    show_change_link = True


class TagInline(admin.TabularInline):
    """Inline для модели метки товара"""

    model = Product.tags.through
    extra = 0
    verbose_name = "Tag"
    verbose_name_plural = "Tags"


class ProductReviewInline(admin.StackedInline):
    """Inline для модели отзыва о товаре"""

    model = ProductReview
    extra = 0
    verbose_name = "Review"
    verbose_name_plural = "Reviews"
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 3, "cols": 80})},
    }


class ProductSpecificationsInline(admin.TabularInline):
    """Inline для модели спецификации товара"""

    model = ProductSpecification
    extra = 0
    verbose_name = "Specification"
    verbose_name_plural = "Specifications"


@action(description="Добавить в ограниченный тираж")
def set_limited(modeladmin, request, queryset) -> None:
    """Добавляет товар в ограниченный тираж"""

    queryset.update(limited=True)


@action(description="Убрать из ограниченного тиража")
def unset_limited(modeladmin, request, queryset) -> None:
    """Удаляет товар из ограниченного тиража"""

    queryset.update(limited=False)


@action(description="Добавить бесплатную доставку")
def set_free_delivery(modeladmin, request, queryset) -> None:
    """Добавляет бесплатную доставку товара"""

    queryset.update(freeDelivery=True)


@action(description="Убрать бесплатную доставку")
def unset_free_delivery(modeladmin, request, queryset) -> None:
    """Удаляет бесплатную доставку товара"""

    queryset.update(freeDelivery=False)


@action(description="Сделать доступным")
def set_available(modeladmin, request, queryset) -> None:
    """Сделать товар доступным"""

    queryset.update(available=True)


@action(description="Сделать недоступным")
def set_unavailable(modeladmin, request, queryset) -> None:
    """Сделать товар недоступным"""

    queryset.update(available=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка товара"""

    change_list_template = "products_app/change_list.html"
    list_display = (
        "id",
        "title",
        "price",
        "count",
        "date",
        "freeDelivery",
        "limited",
        "available",
    )
    list_display_links = (
        "id",
        "title",
    )
    search_fields = (
        "title",
        "description",
    )
    actions = [
        set_limited,
        unset_limited,
        set_free_delivery,
        unset_free_delivery,
        set_available,
        set_unavailable,
    ]
    inlines = (
        ProductImageInline,
        TagInline,
        ProductReviewInline,
        ProductSpecificationsInline,
    )
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 3, "cols": 80})},
    }
    fieldsets = (
        (
            None,
            {
                "fields": ["title", "category", "price", "count"],
            },
        ),
        (
            "Advanced information",
            {
                "fields": [
                    "description",
                    "fullDescription",
                    "freeDelivery",
                    "limited",
                    "available",
                ],
                "classes": ["collapse"],
            },
        ),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Изменяем queryset, чтобы показать только нужные объекты.

        * в данном случае получаем значения поля 'category' у которых есть 'parent'
        """
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(parent__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def add_product_with_form(self, request: HttpRequest):
        """Функция добавления товаров через web-форму"""

        if request.method == "GET":
            product_form = ProductAddForm()
            product_image_form = ProductImageForm()
            context = {
                "product_form": product_form,
                "product_image_form": product_image_form,
            }
            return render(request, "admin/product_create.html", context)

        elif request.method == "POST":
            product_form = ProductAddForm(request.POST)
            product_image_form = ProductImageForm(request.POST, request.FILES)

            if not product_form.is_valid() or not product_image_form.is_valid():
                context = {
                    "product_form": product_form,
                    "product_image_form": product_image_form,
                }
                return render(
                    request,
                    "admin/product_create.html",
                    context,
                    status=400,
                )

            product: Product = product_form.save()
            product_image: ProductImage = product_image_form.save(commit=False)
            product_image.product = product
            product_image.save()

            self.message_user(request, f"Товар '{product.title}' добавлен")
            return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("product-add/", self.add_product_with_form, name="add_product"),
        ]
        return new_urls + urls


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Админка изображения товара"""

    list_display = (
        "id",
        "product",
        "src",
        "alt",
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Админка отзыва о товаре"""

    list_display = (
        "id",
        "product",
        "rate",
        "author",
        "email",
        "text",
        "date",
    )
    list_display_links = ("product",)

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        if user.groups.filter(name__in=["admins", "seller_assistants"]):
            return qs
        return qs.filter(user=request.user)


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    """Админка спецификации товара"""

    list_display = (
        "id",
        "name",
        "value",
        "product",
    )


class SaleItemsInline(admin.TabularInline):
    """Inline элементов распродажи"""

    model = SaleItems
    extra = 0
    verbose_name = "Товар на распродаже"
    verbose_name_plural = "Товары на распродаже"


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    """Админка распродажи"""

    list_display = (
        "id",
        "name",
        "short_description",
        "is_active",
    )
    list_display_links = ("name",)
    inlines = (SaleItemsInline,)

    def short_description(self, obj) -> str:
        """Получаем короткое описание распродажи"""

        if len(obj.description) < 120:
            return obj.description
        return obj.description[:120] + "..."
