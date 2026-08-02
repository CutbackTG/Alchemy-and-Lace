from django.shortcuts import get_object_or_404, render

from .models import Collection, Product


def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related("images", "collections")
    collections = Collection.objects.all()
    collection_slug = request.GET.get("collection")

    if collection_slug:
        products = products.filter(collections__slug=collection_slug)

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": products.distinct(),
            "collections": collections,
            "current_collection": collection_slug,
            "active_menu_item": "gallery",
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("images", "collections"),
        slug=slug,
        is_active=True,
    )
    return render(
        request,
        "catalog/product_detail.html",
        {"product": product, "active_menu_item": "gallery"},
    )
