import random
from datetime import datetime
from decimal import Decimal

from drf_spectacular import utils
from rest_framework import serializers

from mainsite.main_logger import logger
from orders_app.models import Order, OrderProduct, Payment
from products_app.serializers import ProductShortSerializer


class ItemsFromBasketSerializer(serializers.Serializer):
    """Сериализатор данных из корзины"""

    id = serializers.IntegerField(min_value=1, label="product ID")
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
        coerce_to_string=False,
        label="product price",
    )
    count = serializers.IntegerField(min_value=1, label="product count")


class OrderDeliveryInfoSerializer(serializers.ModelSerializer):
    """Сериализатор информации о доставке заказа"""

    class Meta:
        model = Order
        fields = (
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "city",
            "address",
        )

    deliveryType = serializers.ChoiceField(
        choices=Order.OrderDeliveryTypeChoices.labels,
    )
    paymentType = serializers.ChoiceField(
        choices=Order.OrderPaymentTypeChoices.labels,
    )

    def validate_city(self, value):
        """Валидатор значения 'city"""

        if not value:
            raise serializers.ValidationError("city is required")
        return value

    def validate_address(self, value):
        """Валидатор значения 'address"""

        if not value:
            raise serializers.ValidationError("address is required")
        return value

    def update(self, instance, validated_data):
        """Обновление заказа сведениями о доставке"""

        instance.fullName = validated_data.get("fullName", instance.fullName)
        instance.email = validated_data.get("email", instance.email)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.city = validated_data.get("city", instance.city)
        instance.address = validated_data.get("address", instance.address)

        delivery_type_label = validated_data.get("deliveryType")
        if delivery_type_label:
            delivery_type_value = Order.OrderDeliveryTypeChoices.get_value_by_label(
                delivery_type_label
            )
            instance.deliveryType = delivery_type_value

        payment_type_label = validated_data.get("paymentType")
        if payment_type_label:
            payment_type_value = Order.OrderPaymentTypeChoices.get_value_by_label(
                payment_type_label
            )
            instance.paymentType = payment_type_value

        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор заказа"""

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        ]

    deliveryType = serializers.CharField(
        source="get_deliveryType_display", read_only=True
    )
    paymentType = serializers.CharField(
        source="get_paymentType_display", read_only=True
    )
    status = serializers.CharField(source="get_status_display", read_only=True)
    totalCost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
        coerce_to_string=False,
    )
    products = serializers.SerializerMethodField()

    @utils.extend_schema_field(field=ProductShortSerializer(many=True))
    def get_products(self, instance):
        """
        Получаем список товаров с указанием их количества в заказе
        и общую цену на момент покупки
        """

        items = []
        order_items = instance.products.all()
        for item in order_items:

            # Устанавливаем количество товара в заказе
            item.product.count = item.count

            # Устанавливаем общую цену на момент покупки
            item.product.price = item.price

            items.append(item.product)

        products = ProductShortSerializer(items, many=True).data
        return products


class PaymentPayloadSerializer(serializers.ModelSerializer):
    """Сериализатор данных об оплате из запроса"""

    class Meta:
        model = Payment
        exclude = ["order"]


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор оплаты"""

    class Meta:
        model = Payment
        fields = ("number", "name", "month", "year", "code", "order")

    def create(self, validated_data) -> Payment:
        """Создание объекта оплаты"""

        payment = Payment(**validated_data)
        payment.save()
        logger.debug("Payment is created")
        return payment

    def update(self, instance, validated_data) -> Payment:
        """Обновление объекта оплаты провалидированными данными"""

        logger.debug("validated_data: %s", validated_data)
        instance.number = validated_data.get("number", instance.number)
        instance.name = validated_data.get("name", instance.name)
        instance.month = validated_data.get("month", instance.month)
        instance.year = validated_data.get("year", instance.year)
        instance.code = validated_data.get("code", instance.code)
        instance.save()
        logger.debug("Payment updated: %s", instance)
        return instance

    def validate_number(self, value: str) -> str:
        """
        Валидация номера карты для оплаты

        * должны быть указаны только цифры
        * должно быть не менее 1 и не более 8 цифр
        * цифровая последовательность должна быть четной
        * цифровая последовательность не должна оканчиваться нулём
        """

        if not value.isdigit():
            raise serializers.ValidationError("Is not a digit")
        if not 0 < len(value) < 9:
            raise serializers.ValidationError("Is not a valid length")

        # Проверка на нечётность или ноль в конце
        odd = int(value) % 2 == 1
        last_digit = int(value) % 10
        if odd or last_digit == 0:
            payment_error_number = random.randint(1, 100)
            raise serializers.ValidationError(
                "Payment error №{}: Card number odd or have trailing zero".format(
                    payment_error_number
                ),
            )
        return value

    def validate_name(self, value: str) -> str:
        """
        Валидация имени

        * должны быть использованы только буквы
        """

        for word in value.split(" "):
            if not word.isalpha():
                raise serializers.ValidationError("Is not a valid name")
        return value

    def validate_month(self, value) -> str:
        """
        Валидация месяца

        * должны быть указаны только цифры
        * должны быть 2 цифры, например для марта указывается '03'
        * значение должно соответствовать порядковым номерам месяцев года
        """

        if not value.isdigit():
            raise serializers.ValidationError("Is not a digit")
        if not len(value) == 2:
            raise serializers.ValidationError("Is not a valid length")
        if int(value) not in range(1, 13):
            raise serializers.ValidationError("Is not a valid month")
        return value

    def validate_year(self, value) -> str:
        """
        Валидация года

        * должны быть указаны только цифры
        * должны быть указаны или 2, или 4 цифры
        * значение не должно быть из будущего
        """

        if not value.isdigit():
            raise serializers.ValidationError("Is not a digit")
        if len(value) == 2:
            value = "20" + value
        if not len(value) == 4:
            raise serializers.ValidationError(
                "Is not a valid length. \
                Place 4 digits or last 2 digits of the year"
            )
        if int(value) > datetime.now().year:
            raise serializers.ValidationError(
                "Year cannot be greater than current year"
            )
        return value

    def validate_code(self, value):
        """
        Валидация кода

        * должны быть указаны только цифры
        * должны быть указаны 3 цифры
        """

        if not value.isdigit():
            raise serializers.ValidationError("Is not a digit")
        if not len(value) == 3:
            raise serializers.ValidationError("Is not a valid length")
        return value
