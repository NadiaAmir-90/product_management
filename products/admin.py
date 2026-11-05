from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "availability", "updated_at")
    list_filter = ("availability", "category")
    search_fields = ("title", "product_url")