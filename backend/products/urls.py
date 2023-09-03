from django.urls import path

from .views import CategoryDetailView, ProductDetailView

urlpatterns = [
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category"),
    path("p/<slug:product_type>/<slug:slug>/", ProductDetailView.as_view(), name="product"),
]
