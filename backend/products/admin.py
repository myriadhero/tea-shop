from django.contrib import admin

from .models import Category, Product, ProductType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ["name"]}


@admin.register(ProductType)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "quantity")
    prepopulated_fields = {"slug": ["name"]}
