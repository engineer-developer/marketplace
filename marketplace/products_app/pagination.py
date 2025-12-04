from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация"""

    """Custom pagination class"""

    page_size = 10
    max_page_size = 100
    page_query_param = "currentPage"

    def get_paginated_response(self, data):
        """Получаем разбитый на страницы ответ"""

        return Response(
            {
                "items": data,
                "currentPage": self.page.number if self.page else 1,
                "lastPage": self.page.paginator.num_pages if self.page else 1,
            }
        )

    def get_paginated_response_schema(self, schema):
        """Получаем схему ответа с разбивкой по страницам"""

        return {
            "type": "object",
            "required": ["count", "items"],
            "properties": {
                "items": schema,
                "currentPage": {
                    "type": "integer",
                    "example": 1,
                },
                "lastPage": {
                    "type": "integer",
                    "example": 5,
                },
            },
        }


class ProductPagination(CustomPagination):
    """Пагинация товаров"""

    # Задаем название query-параметра для определения количества
    # выводимых товаров на страницу
    page_size_query_param = "limit"


class SalesProductPagination(CustomPagination):
    """Sales Product pagination"""

    pass
