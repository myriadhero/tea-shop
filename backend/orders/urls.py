from django.urls import path

from .views import OrderSuccessPageView, StripeWebhookView

urlpatterns = [
    path("stripe-webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
    path("success/", OrderSuccessPageView.as_view(), name="order-success"),
]
