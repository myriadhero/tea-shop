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
from .models import Address, Order, SessionOrders

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutPageView(TemplateView):
    template_name = "orders/checkout.html"

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
                context["stripeDefaultAddressValues"] = {"address": address.to_dict()}
            except ObjectDoesNotExist:
                pass

        # reuse existing order/stripe payment intent if possible
        if (
            order := Order.objects.filter(
                id=self.request.session.get("order_id")
            ).first()
        ) and order.payment_status == Order.Status.CREATED:
            order.update_from_cart(cart)

            context["stripe_client_secret"] = order.payment_intent_client_secret
            context["cart"] = order.cart
            return context

            # TODO: clear out the canceled orders from DB after some time
            # TODO: also cancel stale payment intents/orders

        # new order created from this point on
        order = Order.create_from_cart(cart)
        # TODO: allow user to access order summary for some time using session
        # maybe need to think about whether incomplete orders should be included
        if not user.is_authenticated:
            SessionOrders(self.request).add_order(order)

        context["cart"] = order.cart
        context["stripe_client_secret"] = order.payment_intent_client_secret
        self.request.session["order_id"] = order.id

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        if not context.get("cart"):
            return HttpResponseRedirect(reverse("cart_page"))
        return self.render_to_response(context)


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

            order.update_details(form)

            if request.user.is_authenticated:
                order.user = request.user
                order.save()

                if form.cleaned_data["save_address"]:
                    try:
                        user_address: Address = request.user.address
                        user_address.update_from_form(form)

                    except ObjectDoesNotExist:
                        Address.create_from_form(form, request.user)

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
            order = Order.objects.filter(payment_intent_id=payment_intent["id"]).first()
            if not order.payment_status == Order.Status.SUCCESS:
                order.payment_status = Order.Status.SUCCESS  # 🎉
                if live_cart := order.live_cart:
                    # TODO: ideally i want to delete only the paid for items from the cart
                    # cart will be deleted on webhook, success page will poll for order status confirmation in case webhook arrives late
                    live_cart.delete()
                order.save()

            # TODO: send email to customer

        # ... handle other event types
        else:
            print(f"Unhandled event type {event['type']}")

        return JsonResponse(success=True)


class OrderSuccessPageView(TemplateView):
    template_name = "orders/success_page.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # TODO: need to reimagine this view to poll for order status confirmation in case webhook arrives late

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

        # TODO: create an order summary page to redirect to
        # for now can just leave the page as is

        return super().get(request, *args, **kwargs)
