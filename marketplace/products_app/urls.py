from django.urls import path

from products_app.views import (
    LimitedProductsListAPIView,
    PopularProductsListAPIView,
    ProductDetailAPIView,
    ProductReviewCreateAPIView,
    ProductsShortListAPIView,
    FavoriteCategoriesProducts,
    SalesProductsApiView,
)

app_name = "products_app"


urlpatterns = [
    path(
        "catalog",
        ProductsShortListAPIView.as_view(),
        name="products_short_list",
    ),
    path(
        "product/<int:pk>/reviews",
        ProductReviewCreateAPIView.as_view(),
        name="product_review_create",
    ),
    path(
        "product/<int:pk>",
        ProductDetailAPIView.as_view(),
        name="product_detail",
    ),
    path(
        "banners",
        FavoriteCategoriesProducts.as_view(),
        name="favorite_categories_products_list",
    ),
    path(
        "products/popular",
        PopularProductsListAPIView.as_view(),
        name="popular_products_list",
    ),
    path(
        "products/limited",
        LimitedProductsListAPIView.as_view(),
        name="limited_products_list",
    ),
    path(
        "sales",
        SalesProductsApiView.as_view(),
        name="sales_products_list",
    ),
]
