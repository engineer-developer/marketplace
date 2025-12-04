from django.test import TestCase
from django.urls import reverse
from catalog_app.models import Category


class TagsListViewTests(TestCase):
    fixtures = ["db_data_fixture.json"]

    def test_can_get_tags_by_category_pk(self):
        """
        Тест - возможно получить список меток товаров
        по атрибуту 'pk' категории товара
        """
        required_fields = [
            "id",
            "name",
        ]

        categories = Category.objects.all()
        for category in categories:
            if category.parent:
                response = self.client.get(
                    path=reverse("tags_app:tags_with_category_list"),
                    query_params={"category": category.pk},
                )
                self.assertEqual(response.status_code, 200)

                tags_data = response.json()
                for tag in tags_data:
                    self.assertListEqual(required_fields, list(tag.keys()))
