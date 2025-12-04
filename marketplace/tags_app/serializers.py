from rest_framework.serializers import ModelSerializer

from tags_app.models import Tag


class TagSerializer(ModelSerializer):
    """Сериализатор данных метки"""

    class Meta:
        model = Tag
        fields = ("id", "name")


class TagNameSerializer(ModelSerializer):
    """Сериализатор имени метки"""

    class Meta:
        model = Tag
        fields = ("name",)
