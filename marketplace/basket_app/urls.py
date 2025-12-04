from django.urls import path

from basket_app.views import BasketAPIView


app_name = "basket_app"

urlpatterns = [
    path("basket", BasketAPIView.as_view(), name="basket"),
]
