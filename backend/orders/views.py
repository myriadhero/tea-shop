from typing import Any

import stripe
from cart.models import Cart
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
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
        client_secret = intent.client_secret

        context["stripe_client_secret"] = client_secret
        self.request.session["client_secret"] = client_secret

        return context


class OrderSuccessPageView(TemplateView):
    template_name = "orders/order_page.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["success"] = "Yes 🦔"

        return context


class CheckoutDetailsUpdateView(View):
    def post(self, request: HttpRequest):
        return JsonResponse(success=True)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request: HttpRequest):
        event = None
        payload = request.data
        sig_header = request.headers["STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            raise e
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise e

        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            # ... handle other event types
        else:
            print("Unhandled event type {}".format(event["type"]))

        return JsonResponse(success=True)
