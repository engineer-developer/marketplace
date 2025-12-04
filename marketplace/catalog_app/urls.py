from django.urls import path

from catalog_app.views import CategoryListAPIView


app_name = "catalog_app"

urlpatterns = [
    path("categories", CategoryListAPIView.as_view(), name="categories_list"),
]
