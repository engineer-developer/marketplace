from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from basket_app.models import BasketItem
from mainsite.main_logger import logger
from products_app.serializers import ProductShortSerializer
from products_app.models import SaleItems


class BasketItemSerializer(serializers.ModelSerializer):
    """Сериализатор элементов корзины"""

    class Meta:
        model = BasketItem
        fields = ("id", "quantity", "product")
        depth = 1

    product = serializers.SerializerMethodField(method_name="get_product")

    @extend_schema_field(field=ProductShortSerializer)
    def get_product(self, instance: BasketItem):
        """Получение товара с обновленным количеством и ценой"""

        # Замена количества товаров на складе на количество товаров в корзине
        instance.product.count = instance.quantity

        # Если товар участвует в распродаже к нему применяется скидка
        sale_items = SaleItems.objects.select_related("product").filter(
            product=instance.product
        )
        if sale_items.exists():
            sale_price = min([item.salePrice for item in sale_items])
            logger.debug("sale_price: %s", sale_price)

            # Замена исходной цены товара на цену со скидкой по распродаже
            instance.product.price = sale_price

        serializer = ProductShortSerializer(instance.product)
        return serializer.data


class ProductAddOrDeleteSerializer(serializers.Serializer):
    """Сериализатор данных для добавления или удаления товаров"""

    id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
