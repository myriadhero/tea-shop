from typing import Any, Optional

import stripe
from cart.models import Cart
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .models import Address, FrozenCart, Order

stripe.api_key = settings.STRIPE_SECRET_KEY

# TODO: refactor logic in views to models


def carts_have_same_items(cart: Cart, frozen_cart: FrozenCart) -> bool:
    if cart.cartitem_set.count() != frozen_cart.frozencartitem_set.count():
        return False

    for cart_item in cart.cartitem_set.all():
        frozen_cart_item = frozen_cart.frozencartitem_set.filter(
            product=cart_item.product
        ).first()
        if not frozen_cart_item or cart_item.quantity != frozen_cart_item.quantity:
            return False

    return True


class OrderPageView(TemplateView):
    template_name = "orders/order_page.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # get cart but do not pass it to context, only pass frozen cart on this page
        cart = Cart.get_request_cart(self.request)

        # no cart, no order
        if not cart:
            return context

        # helper context variables
        context["success_url"] = self.request.build_absolute_uri(
            reverse("order-success")
        )
        if (user := self.request.user).is_authenticated:
            try:
                address: Optional[Address] = user.address
                context["stripeDefaultAddressValues"] = address.to_dict()
            except ObjectDoesNotExist:
                pass

        # reuse existing order if possible
        if (
            order := Order.objects.filter(
                id=self.request.session.get("order_id")
            ).first()
        ) and order.payment_status == Order.Status.CREATED:
            if order.created > cart.updated and carts_have_same_items(cart, order.cart):
                context["stripe_client_secret"] = order.payment_intent
                context["cart"] = order.cart
                return context
            # cancel order if cart was updated
            stripe.PaymentIntent.cancel(order.payment_intent)
            # TODO: clear out the canceled orders from DB after some time
            order.payment_status = Order.Status.CANCELED

        # new order created from this point on
        frozen_cart = FrozenCart.create_from_cart(cart)
        context["cart"] = frozen_cart

        context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY
        intent = stripe.PaymentIntent.create(
            amount=frozen_cart.total_price.amount,
            currency="AUD",
            automatic_payment_methods={
                "enabled": True,
            },
        )
        client_secret = intent.client_secret
        context["stripe_client_secret"] = client_secret

        order = Order.objects.create(cart=frozen_cart, payment_intent=client_secret)
        self.request.session["order_id"] = order.id

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        if not context["cart"]:
            return HttpResponseRedirect(reverse("cart"))
        return self.render_to_response(context)


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
