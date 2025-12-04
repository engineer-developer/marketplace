from django.urls import path, include

from tags_app.views import TagsListByCategoryApiView


app_name = "tags_app"

urlpatterns = [
    path("tags", TagsListByCategoryApiView.as_view(), name="tags_with_category_list"),
]