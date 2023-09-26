from typing import Any

import stripe
from cart.models import Cart
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.views.generic import TemplateView

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderPageView(TemplateView):
    template_name = "orders/order_page.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart.get_request_cart(
            self.request, create_cart=kwargs.get("create_cart", False)
        )
        context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY

        intent = stripe.PaymentIntent.create(
            amount=1999,
            currency="AUD",
            automatic_payment_methods={
                "enabled": True,
            },
        )
        context["stripe_client_secret"] = intent.client_secret

        return context


class CheckoutDetailsUpdateView(View):
    def post(self, request: HttpRequest):
        pass
