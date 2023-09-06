from django.views.generic import DetailView, ListView, TemplateView

from .models import Category, Product, ProductType


class AllProductsView(TemplateView):
    template_name = "products/all_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        return context


class FeaturedProductsView(TemplateView):
    template_name = "products/featured.html"


class CategoryDetailView(DetailView):
    template_name = "products/by_category.html"
    context_object_name = "category"
    model = Category


class ProductTypeDetailView(DetailView):
    template_name = "products/by_type.html"
    context_object_name = "ptype"
    model = ProductType


class ProductDetailView(DetailView):
    template_name = "products/product_detail.html"
    context_object_name = "product"
    model = Product
