from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema

from catalog_app.models import Category
from catalog_app.serializers import CategorySerializer


@extend_schema(
    summary="Get catalog menu",
    description="get catalog menu",
    tags=["catalog"],
)
class CategoryListAPIView(ListAPIView):
    """Представление списка категорий"""

    queryset = (
        Category.objects.filter(available=True)
        .filter(parent__isnull=True)
        .select_related("image")
        .prefetch_related("subcategories__image")
    )
    serializer_class = CategorySerializer
    pagination_class = None
