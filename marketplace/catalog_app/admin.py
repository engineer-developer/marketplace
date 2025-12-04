from django.contrib import admin
from django.contrib.admin.decorators import action
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
from django import forms
from django.db import models

from catalog_app.forms import CSVImportForm, JsonImportForm
from catalog_app.models import Category, CategoryImage
from catalog_app.utils import save_csv_categories, save_json_categories
from products_app.models import Product


class ProductInline(admin.TabularInline):
    model = Product
    fields = ("title", "price", "count")
    readonly_fields = ("title", "price", "count")
    extra = 0
    show_change_link = True
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 3, "cols": 80})},
    }

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=...):
        return False


@action(description="Добавить в избранные")
def set_favorite(modeladmin, request, queryset) -> None:
    """Действие в админке для добавления категорий в избранные"""

    queryset.update(favorite=True)


@action(description="Убрать из избранных")
def unset_favorite(modeladmin, request, queryset) -> None:
    """Действие в админке для удаления категорий из избранных"""

    queryset.update(favorite=False)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка категорий"""

    change_list_template = "catalog_app/change_list.html"
    list_display = ("id", "title", "parent", "favorite", "image")
    list_display_links = ("title", "parent", "favorite", "image")
    search_fields = ("title",)
    list_per_page = 30
    paginator = Paginator
    inlines = (ProductInline,)
    actions = [set_favorite, unset_favorite]

    def import_csv(
        self, request: HttpRequest
    ) -> None | HttpResponseRedirect | HttpResponse:
        """Метод импорта категорий из CSV файла"""

        if request.method == "GET":
            form = CSVImportForm()
            context = {"form": form}
            return render(request, "admin/csv_form.html", context)
        elif request.method == "POST":
            form = CSVImportForm(request.POST, request.FILES)
            if not form.is_valid():
                context = {"form": form}
                return render(request, "admin/csv_form.html", context, status=400)

            result = save_csv_categories(
                file=form.files["csv_file"].file,
                encoding=request.encoding,
            )
            if not result:
                self.message_user(
                    request,
                    f"Successfully imported {len(result)} entries from CSV.",
                )
            else:
                self.message_user(request, "New entries not found.")

            return redirect("..")

    def import_json(self, request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        """Метод импорта категорий из JSON файла"""

        if request.method == "GET":
            form = JsonImportForm()
            context = {"form": form}
            return render(request, "admin/json_form.html", context)
        elif request.method == "POST":
            form = JsonImportForm(request.POST, request.FILES)
            if not form.is_valid():
                context = {"form": form}
                return render(request, "admin/json_form.html", context, status=400)

            result = save_json_categories(
                file=form.files["json_file"].file,
                encoding=request.encoding,
            )
            if result:
                self.message_user(
                    request,
                    f"Successfully imported {len(result)} entries from JSON.",
                )
            else:
                self.message_user(request, "New entries not found.")

        return redirect("..")

    def get_urls(self) -> list:
        """Обновление urls с учетом добавления методов import_csv и import_json"""

        urls = super().get_urls()
        new_urls = [
            path("import-csv/", self.import_csv, name="import_categories_csv"),
            path("import-json/", self.import_json, name="import_categories_json"),
        ]
        return new_urls + urls


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    """Админка изображений категорий"""

    ordering = ("category",)
    list_display = ("id", "category", "src", "alt")
    list_display_links = (
        "category",
        "src",
    )
    search_fields = ("src", "alt")

    def category(self, obj):
        return obj.category.title
