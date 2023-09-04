from django.urls import path

from .views import (
    AllProductsView,
    CategoryDetailView,
    ProductDetailView,
    ProductTypeDetailView,
)

urlpatterns = [
    path("", AllProductsView.as_view(), name="all_products"),
    path(
        "category/<slug:slug>/",
        CategoryDetailView.as_view(),
        name="products_by_category",
    ),
    path("<slug:slug>/", ProductTypeDetailView.as_view(), name="products_by_type"),
    path(
        "<slug:product_type>/<slug:slug>/",
        ProductDetailView.as_view(),
        name="product_details",
    ),
]
