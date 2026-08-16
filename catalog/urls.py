from django.urls import path

from . import views


app_name = "catalog"


urlpatterns = [
    path("", views.shop, name="shop"),

    path(
        "bag/",
        views.bag,
        name="bag",
    ),

    path(
        "bag/remove/<path:line_id>/",
        views.remove_from_bag,
        name="remove_from_bag",
    ),

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

    path(
        "<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
]