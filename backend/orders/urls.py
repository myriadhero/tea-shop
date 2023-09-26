from django.urls import path

from .views import CheckoutDetailsUpdateView

urlpatterns = [
    path("", CheckoutDetailsUpdateView.as_view(), name="checkout_update_details"),
]
