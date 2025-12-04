from typing import Any

from django import forms
from django_stubs_ext import monkeypatch

from products_app.models import Product, ProductImage
from catalog_app.models import Category


monkeypatch()


class ProductAddForm(forms.ModelForm[Product]):
    """Форма для добавления товара"""

    class Meta:
        model = Product
        fields = [
            "category",
            "title",
            "price",
            "count",
            "description",
            "fullDescription",
            "freeDelivery",
            "limited",
            "available",
        ]
        widgets = {
            "category": forms.Select(
                attrs={
                    "class": "form-control form-select form-select-sm",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control form-text",
                    "placeholder": "Введите название",
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Введите цену"}
            ),
            "count": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Введите количество"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Введите описание",
                }
            ),
            "fullDescription": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Введите полное описание",
                }
            ),
            "freeDelivery": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "limited": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределение init для ограничения значений поля category,
        чтобы форма отображала только подкатегории
        """
        super().__init__(*args, **kwargs)
        category_field = self.fields["category"]
        if hasattr(category_field, "queryset"):
            category_field.queryset = Category.objects.filter(parent__isnull=False)
        else:
            raise ValueError("Поле category должно быть ModelChoiceField")


class ProductImageForm(forms.ModelForm[ProductImage]):
    class Meta:
        model = ProductImage
        fields = ("src",)
        widgets = {
            "src": forms.FileInput(attrs={"class": "form-control"}),
        }
