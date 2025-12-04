import datetime
from decimal import Decimal

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict
from drf_spectacular.utils import extend_schema_field

from products_app.models import (
    Product,
    ProductImage,
    ProductReview,
    ProductSpecification,
    SaleItems,
)
from tags_app.serializers import TagNameSerializer, TagSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    """Сериализатор данных изображения товара"""

    class Meta:
        model = ProductImage
        fields = ("src", "alt")


class ProductShortSerializer(serializers.ModelSerializer):
    """Сериализатор данных товара (короткий)"""

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        )

    @staticmethod
    def get_review_count(product: Product) -> int:
        """Получение количества отзывов"""

        return product.reviews.count()

    reviews = serializers.SerializerMethodField(method_name="get_review_count")
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    rating = serializers.DecimalField(
        coerce_to_string=False, max_digits=5, decimal_places=2
    )


class ProductSpecificationSerializer(serializers.ModelSerializer):
    """Сериализатор спецификации товара"""

    class Meta:
        model = ProductSpecification
        fields = ("name", "value")


class ProductReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва о товаре"""

    class Meta:
        model = ProductReview
        fields = (
            "author",
            "email",
            "text",
            "rate",
            "date",
        )


class ProductFullSerializer(serializers.ModelSerializer):
    """Сериализатор данных товара (полный)"""

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        )

    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagNameSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)


class SaleItemsSerializer(serializers.ModelSerializer):
    """Сериализатор элементов распродажи"""

    class Meta:
        model = SaleItems
        fields = (
            "id",
            "price",
            "salePrice",
            "dateFrom",
            "dateTo",
            "title",
            "images",
        )

    id = serializers.SerializerMethodField(method_name="get_id")
    price = serializers.SerializerMethodField(method_name="get_price")
    dateFrom = serializers.SerializerMethodField(method_name="get_dateFrom")
    dateTo = serializers.SerializerMethodField(method_name="get_dateTo")
    title = serializers.SerializerMethodField(method_name="get_title")
    images = serializers.SerializerMethodField(method_name="get_images")

    def get_id(self, obj) -> int:
        """Получение id товара"""

        return obj.product.id

    def get_price(self, obj) -> Decimal:
        """Получение цены товара"""

        return obj.product.price

    def get_title(self, obj) -> str:
        """Получение названия товара"""

        return obj.product.title

    @extend_schema_field(field=ProductImageSerializer(many=True))
    def get_images(self, obj) -> list[ReturnDict]:
        """Получение списка данных о всех изображениях товара"""

        images = obj.product.images.all()
        images_data = [ProductImageSerializer(image).data for image in images]
        return images_data

    @staticmethod
    def get_mounth_year_from_date(value: datetime.date) -> str:
        """Получение месяца и года из переданной даты"""

        date_format = "%m-%y"
        return value.strftime(date_format)

    def get_dateFrom(self, obj) -> str:
        """Получение даты начала распродажи"""

        return self.get_mounth_year_from_date(obj.dateFrom)

    def get_dateTo(self, obj) -> str:
        """Получение даты окончания распродажи"""

        return self.get_mounth_year_from_date(obj.dateTo)
