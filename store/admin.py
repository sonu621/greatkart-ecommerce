from django.contrib import admin
from django.utils.html import format_html

from .models import Product, Variation, ReviewRating, ProductGallery


# ---------------- Product Gallery Admin ----------------

@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'image',
        'thumbnail',
    )

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:5px;" />',
                obj.image.url
            )
        return "No Image"

    thumbnail.short_description = "Preview"


# ---------------- Product Gallery Inline ----------------

class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:5px;" />',
                obj.image.url
            )
        return "No Image"

    thumbnail.short_description = "Preview"


# ---------------- Product Admin ----------------

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'price',
        'stock',
        'category',
        'modified_date',
        'is_available',
    )

    prepopulated_fields = {
        'slug': ('product_name',)
    }

    inlines = [
        ProductGalleryInline,
    ]


# ---------------- Variation Admin ----------------

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'variation_category',
        'variation_value',
        'is_active',
    )

    list_editable = (
        'is_active',
    )

    list_filter = (
        'product',
        'variation_category',
        'variation_value',
    )


# ---------------- Review Rating Admin ----------------

@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'rating',
        'review',
        'created_at',
    )