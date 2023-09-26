from django.urls import path

from .views import CheckoutDetailsUpdateView, StripeWebhookView

urlpatterns = [
    path(
        "order-details/",
        CheckoutDetailsUpdateView.as_view(),
        name="checkout_update_details",
    ),
    path("stripe-webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
]
