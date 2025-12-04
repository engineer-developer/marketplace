from rest_framework import serializers

from catalog_app.models import Category, CategoryImage


class CategoryImageSerializer(serializers.ModelSerializer):
    """Сериализатор изображения категории"""

    class Meta:
        model = CategoryImage
        fields = ("src", "alt")

    alt = serializers.SerializerMethodField(method_name="get_alt")

    @staticmethod
    def get_alt(obj) -> str:
        """Метод получения поля 'alt'"""
        if not obj.alt:
            return obj.src.name.rsplit("/", 1)[-1]
        return obj.alt


class SubCategorySerializer(serializers.ModelSerializer):
    """Сериализатор подкатегорий"""

    class Meta:
        model = Category
        fields = ("id", "title", "image")
        depth = 1

    image = CategoryImageSerializer()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории каталога"""

    class Meta:
        model = Category
        fields = ("id", "title", "image", "subcategories")
        depth = 1

    image = CategoryImageSerializer()
    subcategories = SubCategorySerializer(many=True)
