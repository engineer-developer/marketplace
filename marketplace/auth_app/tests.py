from django.test import TestCase
from django.test.client import Client
from django.urls.base import reverse


class AuthTestCase(TestCase):
    fixtures = ["db_data_fixture.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_can_authenticate(self):
        """Тест - возможно залогиниться с именем и паролем"""
        credentials = {
            "username": "mat",
            "password": "123456",
        }

        response = self.client.post(
            path=reverse("auth_app:sign_in"),
            data=credentials,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully sign-in", response.data)
        user = response.renderer_context.get("request").user
        self.assertTrue(user.is_authenticated)
