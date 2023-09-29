from django.urls import path

from .views import CheckoutDetailsUpdateView, OrderSuccessPageView, StripeWebhookView

urlpatterns = [
    path(
        "order-details/",
        CheckoutDetailsUpdateView.as_view(),
        name="checkout_update_details",
    ),
    path("stripe-webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
    path("success/", OrderSuccessPageView.as_view(), name="order-success"),
]
