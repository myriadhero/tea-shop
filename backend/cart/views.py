from django.views.generic import TemplateView

from .models import Cart


class CartPageView(TemplateView):
    template_name = "cart/cart_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart.get_request_cart(self.request)
        return context

    def post(self, request, *args, **kwargs):
        # post is used to update cart
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
