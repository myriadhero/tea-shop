from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from products.models import Product

from .forms import CartItemForm
from .models import Cart


class CartPageView(TemplateView):
    template_name = "cart/cart_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart.get_request_cart(
            self.request, create_cart=kwargs.get("create_cart", False)
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        form = CartItemForm(request.POST)
        if form.is_valid():
            product: Product = get_object_or_404(
                Product, slug=form.cleaned_data["product_slug"]
            )
            remove_from_cart = form.cleaned_data.get("remove_from_cart")

            cart: Cart = Cart.get_request_cart(
                request, create_cart=not remove_from_cart
            )
            if not remove_from_cart:
                cart.add_product(
                    product=product,
                    quantity=form.cleaned_data.get("quantity") or 1,
                    set_quantity=form.cleaned_data.get("set_quantity"),
                )
            elif cart:
                cart.remove_product(product=product)

        return HttpResponseRedirect(reverse("cart_page"))
