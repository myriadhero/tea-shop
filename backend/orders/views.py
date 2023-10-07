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

from .forms import OrderDetailsForm
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
        context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY
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
        # TODO: stripe docs say that i should reuse existing payment intent if possible instead of creating a new one
        # i need to update the payment amount if the cart has changed
        # and create new frozen cart
        # and delete the old frozen cart
        if (
            order := Order.objects.filter(
                id=self.request.session.get("order_id")
            ).first()
        ) and order.payment_status == Order.Status.CREATED:
            if cart.updated > order.cart.updated or not carts_have_same_items(
                cart, order.cart
            ):
                # recreate frozen cart, add it to order and reuse the order and instent
                old_frozen_cart = order.cart
                new_frozen_cart = FrozenCart.create_from_cart(cart)

                if new_frozen_cart.total_price != old_frozen_cart.total_price:
                    intent = stripe.PaymentIntent.modify(
                        order.payment_intent_id,
                        amount=new_frozen_cart.total_price.get_amount_in_sub_unit(),
                    )
                    order.payment_intent_client_secret = intent.client_secret

                order.cart = new_frozen_cart
                order.save()
                old_frozen_cart.delete()

            context["stripe_client_secret"] = order.payment_intent_client_secret
            context["cart"] = order.cart
            return context

            # TODO: clear out the canceled orders from DB after some time
            # TODO: also cancel stale payment intents/orders

        # new order created from this point on
        frozen_cart = FrozenCart.create_from_cart(cart)
        context["cart"] = frozen_cart

        intent = stripe.PaymentIntent.create(
            amount=frozen_cart.total_price.get_amount_in_sub_unit(),
            currency="AUD",
            automatic_payment_methods={
                "enabled": True,
            },
        )
        client_secret = intent.client_secret
        context["stripe_client_secret"] = client_secret

        order = Order.objects.create(
            cart=frozen_cart,
            payment_intent_id=intent.id,
            payment_intent_client_secret=client_secret,
        )
        self.request.session["order_id"] = order.id

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        if not context["cart"]:
            return HttpResponseRedirect(reverse("cart"))
        return self.render_to_response(context)


class OrderSuccessPageView(TemplateView):
    template_name = "orders/success_page.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # ?payment_intent=pi_3NyZ...&payment_intent_client_secret=pi_3NyZ..._secret_ZL0...&redirect_status=succeeded
        # i want to redirect to ?order_id to hide payment intent from url
        # but i also wan to remove order_id from session
        if not (
            (order := Order.objects.filter(id=request.session.get("order_id")).first())
            and order.payment_status == Order.Status.SUCCESS
            and order.payment_intent_client_secret
            == request.GET.get("payment_intent_client_secret")
        ):
            return HttpResponseRedirect(reverse("cart"))

        request.session.pop("order_id")
        Cart.get_request_cart(request).delete()

        # TODO: create an order summary page to redirect to
        # for now can just leave the page as is

        return super().get(request, *args, **kwargs)


class CheckoutDetailsUpdateView(View):
    def post(self, request: HttpRequest):
        form = OrderDetailsForm(request.POST)
        if form.is_valid():
            if (
                not (order_id := request.session.get("order_id"))
                or not (order := Order.objects.filter(id=order_id).first())
                or order.payment_intent_client_secret
                != form.cleaned_data["payment_intent"]
                or order.payment_status != Order.Status.CREATED
            ):
                return JsonResponse(
                    {
                        "success": False,
                        "errors": [
                            "Something went wrong. Please refresh the page and try again."
                        ],
                    }
                )

            order_address = Address.create_from_form(form, order)
            email = form.cleaned_data["email"]

            if request.user.is_authenticated:
                order.user = request.user
                email = request.user.email

                if form.cleaned_data["save_address"]:
                    try:
                        user_address: Address = request.user.address
                        user_address.update_from_form(form)

                    except ObjectDoesNotExist:
                        Address.create_from_form(form, request.user)

            order.email = email
            order.payment_status = Order.Status.PENDING
            order.save()

            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})


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
            order = Order.objects.filter(payment_intent=payment_intent["id"]).first()
            order.payment_status = Order.Status.SUCCESS  # 🎉
            order.save()

            # TODO: send email to customer

        # ... handle other event types
        else:
            print(f"Unhandled event type {event['type']}")

        return JsonResponse(success=True)
