from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from .shopify import (
    add_cart_line,
    create_cart,
    get_collection_by_handle,
    get_product_by_handle,
    get_products,
)


def product_list(request):
    products = get_products()

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": products,
            "active_menu_item": "shop",
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
            "active_menu_item": "shop",
        },
    )


def shop(request):
    return render(
        request,
        "catalog/shop.html",
        {
            "active_menu_item": "shop",
        },
    )


def collection_detail(request, collection_handle):
    collection = get_collection_by_handle(collection_handle)

    if not collection:
        raise Http404("Collection not found.")

    return render(
        request,
        "catalog/collection_detail.html",
        {
            "collection": collection,
            "products": collection["products"]["nodes"],
            "active_menu_item": "shop",
        },
    )


def add_to_bag(request, slug):
    if request.method != "POST":
        return redirect(
            "catalog:product_detail",
            slug=slug,
        )

    product = get_product_by_handle(slug)

    if not product:
        raise Http404("Product not found.")

    variant = product.get("selectedOrFirstAvailableVariant")

    if not variant or not variant.get("availableForSale"):
        messages.error(
            request,
            "This piece is no longer available.",
        )

        return redirect(
            "catalog:product_detail",
            slug=slug,
        )

    variant_id = variant["id"]
    cart_id = request.session.get("shopify_cart_id")

    try:
        if cart_id:
            cart = add_cart_line(
                cart_id,
                variant_id,
                quantity=1,
            )
        else:
            cart = create_cart(
                variant_id,
                quantity=1,
            )

        request.session["shopify_cart_id"] = cart["id"]
        request.session["shopify_checkout_url"] = cart["checkoutUrl"]
        request.session["shopify_cart_quantity"] = cart["totalQuantity"]

        messages.success(
            request,
            f"{product['title']} added to your bag.",
        )

    except RuntimeError:
        messages.error(
            request,
            "We couldn't add that piece to your bag. Please try again.",
        )

    return redirect(
        "catalog:product_detail",
        slug=slug,
    )


def checkout(request):
    checkout_url = request.session.get("shopify_checkout_url")

    if not checkout_url:
        messages.info(
            request,
            "Your bag is empty.",
        )

        return redirect("catalog:shop")

    return redirect(checkout_url)