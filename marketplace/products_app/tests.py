from django.test import TestCase
from django.urls import reverse

from products_app.models import Product
from django.contrib.auth.models import User


class ProductsApiViewTests(TestCase):
    """Тесты для представлений товаров"""

    fixtures = ["db_data_fixture.json"]

    def test_can_get_all_products(self):
        """Тест - возможно получить все товары"""

        products_quantity = Product.objects.all().count()

        response = self.client.get(
            path=reverse("products_app:products_short_list"),
            query_params={"limit": 100},
        )
        self.assertEqual(response.status_code, 200)
        received_items_quantity = len(response.json()["items"])
        self.assertEqual(products_quantity, received_items_quantity)

    def test_can_get_product_full_details(self):
        """Тест - возможно получить полную информацию о товаре по его 'pk'"""

        product_full_required_fields = [
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
        ]
        product: Product | None = Product.objects.first()
        self.assertTrue(product, "Product not found.")
        if product is None:
            return False
        product_pk = product.pk
        response = self.client.get(
            path=reverse(
                "products_app:product_detail",
                kwargs={"pk": product_pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        product_details = response.json()
        self.assertListEqual(
            list(product_details.keys()),
            product_full_required_fields,
        )

    def test_can_get_popular_products(self):
        """Тест - возможно получить популярные товары"""

        response = self.client.get(
            path=reverse("products_app:popular_products_list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)

    def test_can_get_limited_products(self):
        """Тест - возможно получить лимитированные товары"""

        response = self.client.get(
            path=reverse("products_app:limited_products_list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)

    def test_can_create_product_review(self):
        """Тест - возможно создать отзыв на товар"""

        user = User.objects.last()
        self.assertTrue(user, "User not found.")
        if user is None:
            return False

        product = Product.objects.first()
        self.assertTrue(product, "Product not found.")
        if product is None:
            return False

        product_pk = product.pk
        review_data = {
            "author": "Author name",
            "email": "some_email@mail.ru",
            "text": "rewrewrwerewrwerwerewrwerwer",
            "rate": 4,
        }
        self.client.force_login(user)

        response = self.client.post(
            path=reverse(
                "products_app:product_review_create",
                kwargs={"pk": product_pk},
            ),
            data=review_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        received_data = response.json()[0]
        self.assertEqual(received_data["author"], user.get_full_name())
        self.assertEqual(received_data["email"], user.email)
        self.assertEqual(received_data["text"], review_data["text"])
        self.assertEqual(received_data["rate"], review_data["rate"])
