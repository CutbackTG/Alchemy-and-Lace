from django.urls import path

from . import views


app_name = "catalog"


urlpatterns = [
    path("", views.shop, name="shop"),

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    path(
        "collection/<slug:collection_handle>/",
        views.collection_detail,
        name="collection_detail",
    ),

    path(
        "<slug:slug>/add-to-bag/",
        views.add_to_bag,
        name="add_to_bag",
    ),

    path("checkout/", views.checkout, name="checkout"),

    path(
        "<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
]