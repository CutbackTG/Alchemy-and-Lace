from django.http import Http404
from django.shortcuts import render

from .shopify import get_product_by_handle, get_products


def product_list(request):
    products = get_products()

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": products,
            "active_menu_item": "gallery",
        },
    )


def product_detail(request, slug):
    product = get_product_by_handle(slug)

    if not product:
        raise Http404("Product not found.")

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "active_menu_item": "gallery",
        },
    )