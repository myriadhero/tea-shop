from django.views.generic import DetailView, ListView

from .models import Category, Product


class CategoryDetailView(DetailView):
    template_name = "products/category_detail.html"
    context_object_name = "category"
    model = Category


class ProductDetailView(DetailView):
    template_name = "products/product_detail.html"
    context_object_name = "product"
    model = Product
