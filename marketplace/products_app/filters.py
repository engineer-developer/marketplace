import re

import django_filters
from django.db.models import DecimalField, Value, Avg
from django.http.request import QueryDict
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.widgets import BooleanWidget
from rest_framework.filters import OrderingFilter
from django.db.models.aggregates import Count
from django.db.models.functions import Coalesce

from catalog_app.models import Category
from mainsite.main_logger import logger
from products_app.models import Product


class ProductsFilterBackend(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        """
        Функция меняет query-параметры http-запроса
        если они содержат ключи 'filter[param]'

        Например: 'filter[name]' заменяет на 'name'

        Остальные параметры остаются неизменными
        """

        kwargs = super().get_filterset_kwargs(request, queryset, view)
        initial_query_params: QueryDict = kwargs["data"]
        logger.debug("Initial query params: %s", initial_query_params)
        logger.debug("Url query: %s", initial_query_params.urlencode(safe="[]&"))

        updated_query_params = QueryDict(mutable=True)
        filter_pattern = re.compile(r"filter\[(\w*?)]")
        for key, value in initial_query_params.items():
            if value and isinstance(value, str):
                match = filter_pattern.search(key)
                if match:
                    key = match.group(1)
                elif "tags[]" in key:
                    continue
                updated_query_params.appendlist(key, value)

        tags = initial_query_params.getlist("tags[]")
        if tags:
            updated_query_params.setlist("tags[]", tags)

        logger.debug("New query params: %s", updated_query_params)
        kwargs["data"] = updated_query_params
        return kwargs


class ProductFilter(django_filters.FilterSet):
    """Фильтр товаров"""

    # фильтр по имени товара
    name = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    # фильтр по минимальной цене товара
    minPrice = django_filters.NumberFilter(field_name="price", lookup_expr="gte")

    # фильтр по максимальной цене товара
    maxPrice = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # фильтр по наличию бесплатной доставки
    freeDelivery = django_filters.BooleanFilter(
        field_name="freeDelivery", widget=BooleanWidget()
    )

    # фильтр по доступности товара
    available = django_filters.BooleanFilter(
        field_name="available", widget=BooleanWidget()
    )

    # фильтр по категории товара
    category = django_filters.NumberFilter(
        field_name="category", method="select_category"
    )

    def select_category(self, queryset, name, value):
        """Получение категории товара"""

        category = Category.objects.get(pk=value)
        if category.parent is None:
            return queryset.filter(category__id__in=category.subcategories.all())
        return queryset.filter(category__id=value)

    class Meta:
        model = Product
        fields = [
            "name",
            "minPrice",
            "maxPrice",
            "freeDelivery",
            "available",
            "category",
        ]


class ProductOrdering(OrderingFilter):
    """Сортировка товаров"""

    ordering_param = "sort"
    ordering_fields = (
        "price",
        "reviews",
        "date",
        "rating",
    )

    def filter_queryset(self, request, queryset, view):
        """Переопределение метода для применения сортировки с параметром 'sortType"""

        ordering = self.get_ordering(request, queryset, view)
        sort_type = request.query_params.get("sortType", "desc")
        ordering_direction = "" if sort_type == "inc" else "-"

        if ordering:
            ordering_value = ordering[0]

            if ordering_value == "reviews":
                return queryset.annotate(review_count=Count("reviews")).order_by(
                    "{ordering_direction}{ordering_value}".format(
                        ordering_direction=ordering_direction,
                        ordering_value="review_count",
                    )
                )
            elif ordering_value == "rating":
                return queryset.annotate(
                    avg_rating=Coalesce(
                        Avg("reviews__rate"),
                        Value(0),
                        output_field=DecimalField(),
                    )
                ).order_by(
                    "{ordering_direction}{ordering_value}".format(
                        ordering_direction=ordering_direction,
                        ordering_value="avg_rating",
                    )
                )
            return queryset.order_by(
                "{ordering_direction}{ordering_value}".format(
                    ordering_direction=ordering_direction,
                    ordering_value=ordering_value,
                )
            )

        return queryset
