from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from .shopify import (
    add_cart_line,
    create_cart,
    get_cart,
    get_collection_by_handle,
    get_product_by_handle,
    get_products,
    remove_cart_line,
)


CANONICAL_SITE_URL = "https://www.anarchyandlace.co.uk"


def _clear_cart_session(request):
    """
    Remove all Shopify cart information from the Django session.
    """
    request.session.pop("shopify_cart_id", None)
    request.session.pop("shopify_checkout_url", None)
    request.session.pop("shopify_cart_quantity", None)


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

    product_path = reverse(
        "catalog:product_detail",
        kwargs={
            "slug": product["handle"],
        },
    )

    canonical_url = (
        f"{CANONICAL_SITE_URL}{product_path}"
    )

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "canonical_url": canonical_url,
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
    collection = get_collection_by_handle(
        collection_handle
    )

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

    variant = product.get(
        "selectedOrFirstAvailableVariant"
    )

    if not variant or not variant.get(
        "availableForSale"
    ):
        messages.error(
            request,
            "This piece is no longer available.",
        )

        return redirect(
            "catalog:product_detail",
            slug=slug,
        )

    variant_id = variant["id"]

    cart_id = request.session.get(
        "shopify_cart_id"
    )

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

        request.session[
            "shopify_cart_id"
        ] = cart["id"]

        request.session[
            "shopify_checkout_url"
        ] = cart["checkoutUrl"]

        request.session[
            "shopify_cart_quantity"
        ] = cart["totalQuantity"]

        messages.success(
            request,
            f"{product['title']} added to your bag.",
        )

    except RuntimeError:
        messages.error(
            request,
            (
                "We couldn't add that piece to your bag. "
                "Please try again."
            ),
        )

    return redirect(
        "catalog:product_detail",
        slug=slug,
    )


def bag(request):
    cart_id = request.session.get(
        "shopify_cart_id"
    )

    if not cart_id:
        return render(
            request,
            "catalog/bag.html",
            {
                "cart": None,
                "active_menu_item": "shop",
            },
        )

    try:
        cart = get_cart(cart_id)

    except RuntimeError:
        cart = None

    if not cart:
        _clear_cart_session(request)

    else:
        request.session[
            "shopify_checkout_url"
        ] = cart["checkoutUrl"]

        request.session[
            "shopify_cart_quantity"
        ] = cart["totalQuantity"]

    return render(
        request,
        "catalog/bag.html",
        {
            "cart": cart,
            "active_menu_item": "shop",
        },
    )


def remove_from_bag(request, line_id):
    if request.method != "POST":
        return redirect("catalog:bag")

    cart_id = request.session.get(
        "shopify_cart_id"
    )

    if not cart_id:
        return redirect("catalog:bag")

    try:
        cart = remove_cart_line(
            cart_id,
            line_id,
        )

        if cart["totalQuantity"] == 0:
            _clear_cart_session(request)

        else:
            request.session[
                "shopify_checkout_url"
            ] = cart["checkoutUrl"]

            request.session[
                "shopify_cart_quantity"
            ] = cart["totalQuantity"]

    except RuntimeError:
        messages.error(
            request,
            "We couldn't remove that piece from your bag.",
        )

    return redirect("catalog:bag")


def checkout(request):
    checkout_url = request.session.get(
        "shopify_checkout_url"
    )

    if not checkout_url:
        messages.info(
            request,
            "Your bag is empty.",
        )

        return redirect("catalog:shop")

    return redirect(checkout_url)