from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from tags_app.models import Tag
from tags_app.serializers import TagSerializer
from catalog_app.models import Category


@extend_schema(
    summary="Get tags",
    description="Get tags",
    tags=["tags"],
    parameters=[OpenApiParameter(name="category", type=int)],
)
class TagsListByCategoryApiView(ListAPIView):
    """Представление для получения списка меток товара по категории товара"""

    serializer_class = TagSerializer

    def get_queryset(self):
        """Получение списка меток товара отфильтрованных по категории товара"""

        category_id = self.request.GET.get("category", None)
        if not category_id:
            return Tag.objects.all()

        category = Category.objects.get(pk=category_id)
        if category.parent is not None:
            queryset = Tag.objects.filter(products__category__id=category_id)
        else:
            queryset = Tag.objects.filter(
                products__category__id__in=category.subcategories.all()
            )
        return queryset.prefetch_related("products__category").distinct()
