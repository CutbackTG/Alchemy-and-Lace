from django.urls import path

from . import views


app_name = "catalog"


urlpatterns = [
    path("", views.shop, name="shop"),
    path(
        "collection/<slug:collection_handle>/",
        views.collection_detail,
        name="collection_detail",
    ),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
]