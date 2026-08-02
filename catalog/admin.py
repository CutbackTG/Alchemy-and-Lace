from django.contrib import admin

from .models import Collection, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "fabric_origin", "is_active", "updated_at")
    list_filter = ("is_active", "collections")
    search_fields = ("name", "description", "fabric_origin")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("collections",)
    inlines = (ProductImageInline,)
    fields = (
        "name", "slug", "description", "image", "fabric_origin",
        "size", "fit_notes", "care_instructions", "collections", "is_active",
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
