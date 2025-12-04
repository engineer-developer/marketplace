from faker import Faker

from django.db.models.query_utils import Q
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import User

from orders_app.models import Order
from products_app.models import Product


class OrdersTests(TestCase):
    fixtures = ["db_data_fixture.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.first()
        cls.test_client = Client()
        cls.test_client.force_login(user)

    def test_can_get_orders_list(self):
        """Тест - возможно получить список заказов"""

        response = self.test_client.get(
            path=reverse("orders_app:orders_list_or_create"),
        )
        self.assertEqual(response.status_code, 200)

    def test_can_create_order(self):
        """Тест - возможно создать заказ"""

        product = Product.objects.first()
        payload = [
            {
                "id": product.id,
                "count": 1,
                "price": 200,
            }
        ]
        response = self.test_client.post(
            path=reverse("orders_app:orders_list_or_create"),
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def test_can_get_order_by_id(self):
        """Тест - возможно получить заказ по его 'id"""

        order = Order.objects.first()
        response = self.test_client.get(
            path=reverse(
                "orders_app:get_or_update_order",
                kwargs={"id": order.id},
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_can_confirm_order_with_id(self):
        """Тест - возможно подтвердить заказ"""

        fake_user = Faker()
        user_data = {
            "fullName": fake_user.name(),
            "email": fake_user.email(),
            "phone": fake_user.phone_number()[:11],
            "deliveryType": "ordinary",
            "paymentType": "online",
            "city": fake_user.city(),
            "address": fake_user.address(),
        }

        order = Order.objects.filter(~Q(status="PAIDED")).last()
        response = self.test_client.post(
            path=reverse(
                "orders_app:get_or_update_order",
                kwargs={"id": order.id},
            ),
            data=user_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 202)
