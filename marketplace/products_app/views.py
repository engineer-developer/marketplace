import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models.aggregates import Count
from django.db.utils import IntegrityError
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response

from catalog_app.models import Category
from mainsite.handle_errors import handle_serializer_not_valid
from mainsite.main_logger import logger
from products_app.filters import ProductFilter, ProductOrdering, ProductsFilterBackend
from products_app.models import Product, ProductReview, SaleItems
from products_app.pagination import ProductPagination, SalesProductPagination
from products_app.serializers import (
    ProductFullSerializer,
    ProductReviewSerializer,
    ProductShortSerializer,
    SaleItemsSerializer,
)


@extend_schema(
    summary="Get catalog items",
    description="get catalog items",
    tags=["catalog"],
)
class ProductsShortListAPIView(generics.ListAPIView):
    """Представление для получения списка товаров"""

    queryset = Product.objects.all()
    serializer_class = ProductShortSerializer
    pagination_class = ProductPagination
    filter_backends = (
        ProductsFilterBackend,
        ProductOrdering,
    )
    filterset_class = ProductFilter

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Получение списка товаров"""

        popular_tags_ids = request.GET.getlist("tags[]")
        # logger.debug("popular_tags_ids: %s", popular_tags_ids)
        if not popular_tags_ids:
            return super().list(request, *args, **kwargs)

        queryset = (
            self.filter_queryset(self.get_queryset())
            .filter(tags__in=popular_tags_ids)
            .filter(available=True)
            .select_related("category")
            .prefetch_related("images", "tags", "reviews")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    summary="Get catalog item",
    description="get catalog item",
    tags=["product"],
    parameters=[OpenApiParameter(name="id", location="path", type=int)],
    responses={200: ProductFullSerializer},
)
class ProductDetailAPIView(generics.RetrieveAPIView):
    """Представление для получения товара по его 'pk'"""

    queryset = (
        Product.objects.filter(available=True)
        .select_related("category")
        .prefetch_related("images", "tags", "specifications", "reviews")
    )
    serializer_class = ProductFullSerializer


@extend_schema(
    summary="Get banner items",
    description="get banner items",
    tags=["catalog"],
    responses={
        200: OpenApiResponse(
            description="successful operation",
            response=ProductShortSerializer(many=True),
        )
    },
)
class FavoriteCategoriesProducts(generics.ListAPIView):
    """
    Представление для получения списка товаров из избранных категорий
    для показа баннеров
    """

    queryset = Product.objects.all()
    serializer_class = ProductShortSerializer

    # @method_decorator(cache_page(timeout=60 * 2))
    def list(self, request, *args, **kwargs):
        """Получение списка товаров"""

        # Ограничиваем количество отображаемых баннеров с товарами
        view_limit = 3

        products = []
        favorite_categories = Category.objects.filter(favorite=True)[:view_limit]
        for category in favorite_categories:
            product = category.products.filter(available=True).first()
            products.append(product)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get catalog popular items",
    description="get catalog popular items",
    tags=["catalog"],
)
class PopularProductsListAPIView(generics.ListAPIView):
    """
    Представление для получения списка топ-товаров

    * Сортировка осуществляется по количеству покупок товаров
    """

    # Ограничиваем количество отображаемых товаров
    view_limit = 8

    queryset = (
        Product.objects.filter(available=True)
        .annotate(product_in_order_count=Count("orderProduct"))
        .order_by("-product_in_order_count")[:view_limit]
        .select_related("category")
        .prefetch_related("images", "tags", "reviews")
    )
    serializer_class = ProductShortSerializer

    # @method_decorator(cache_page(timeout=60 * 2))
    def list(self, request, *args, **kwargs):
        """Получение списка топ-товаров"""

        return super().list(request, *args, **kwargs)


@extend_schema(
    summary="Get catalog limited items",
    description="get catalog limited items",
    tags=["catalog"],
)
class LimitedProductsListAPIView(generics.ListAPIView):
    """Представление для получения списка товаров с ограниченным тиражом"""

    # Ограничиваем количество отображаемых товаров
    view_limit = 16

    queryset = (
        Product.objects.filter(available=True)
        .filter(limited=True)[:view_limit]
        .select_related("category")
        .prefetch_related("images", "tags", "reviews")
    )
    serializer_class = ProductShortSerializer

    # @method_decorator(cache_page(timeout=60 * 2))
    def list(self, request, *args, **kwargs):
        """Получение списка товаров"""

        return super().list(request, *args, **kwargs)


@extend_schema(
    summary="Post product review",
    description="post product review",
    tags=["product"],
    parameters=[
        OpenApiParameter(
            name="id",
            location="path",
            type=int,
            description="product id",
        )
    ],
    request={
        "application/json": {
            "example": {
                "author": "Annoying Orange",
                "email": "no-reply@mail.ru",
                "text": "rewrewrwerewrwerwerewrwerwer",
                "rate": 4,
                "date": "2023-05-05 12:12",
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="successful operation",
            response=ProductReviewSerializer(many=True),
            examples=[
                OpenApiExample(
                    "Example",
                    value={
                        "author": "Annoying Orange",
                        "email": "no-reply@mail.ru",
                        "text": "rewrewrwerewrwerwerewrwerwer",
                        "rate": 4,
                        "date": "2023-05-05 12:12",
                    },
                    response_only=True,
                ),
            ],
        )
    },
)
class ProductReviewCreateAPIView(generics.CreateAPIView):
    """Представление для создания отзыва на товар"""

    def create(self, request, *args, **kwargs) -> Response:
        """Создание отзыва"""

        # Если пользователь не авторизован выдаст сообщение о том,
        # что нужно авторизоваться, чтобы оставить отзыв
        if not request.user.is_authenticated:
            message = (
                "User is not logged in. Please log in for have ability to make review."
            )
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        product = Product.objects.get(pk=self.kwargs["pk"])
        serializer = ProductReviewSerializer(data=request.data)

        # Проверяем корректность введенных данных
        if not serializer.is_valid():
            return handle_serializer_not_valid(serializer)
        logger.debug("Review data is valid")

        # Проверяем уникальность создаваемого отзыва учитывая поля "product", "email"
        try:
            review: ProductReview = serializer.save(
                product=product,
                user=request.user,
                author=request.user.get_full_name(),
                email=request.user.email,
            )
            logger.debug("Review by %s published", review.author)
        except IntegrityError as exc:
            logger.error("IntegrityError: %s", str(exc))
            return Response(
                data={"Error": "Review with such email already exist"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(data=[serializer.data], status=status.HTTP_200_OK)


@extend_schema(
    summary="Get sales items",
    description="get sales items",
    tags=["catalog"],
)
class SalesProductsApiView(generics.ListAPIView):
    """Представление для получения списка распродаж товаров"""

    queryset = (
        SaleItems.objects.filter(sale__is_active=True)
        .filter(is_active=True)
        .filter(dateFrom__lte=datetime.date.today())
        .filter(dateTo__gte=datetime.date.today())
        .prefetch_related(
            "product",
            "product__images",
        )
    )
    serializer_class = SaleItemsSerializer
    pagination_class = SalesProductPagination
