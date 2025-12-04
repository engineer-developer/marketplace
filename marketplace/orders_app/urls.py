from django.urls import path

from orders_app.views import (
    OrderDetailsApiView,
    OrdersListCreateApiView,
    PaymentApiView,
)


app_name = "orders_app"


urlpatterns = [
    path(
        "orders",
        OrdersListCreateApiView.as_view(),
        name="orders_list_or_create",
    ),
    path(
        "order/<int:id>",
        OrderDetailsApiView.as_view(),
        name="get_or_update_order",
    ),
    path(
        "payment/<int:id>",
        PaymentApiView.as_view(),
        name="payment_api",
    ),
]
