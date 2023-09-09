from django.contrib.sessions.models import Session
from django.views.generic import TemplateView

from .models import Cart


class CartPageView(TemplateView):
    template_name = "cart/cart_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session_key = self.request.session.session_key
        session_cart = Session.objects.get(session_key).cart
        # if db_session.cart.exists():
        #     context["cart"] = db_session.cart

        # anonymous user
        if not self.request.user.is_authenticated:
            context["cart"] = session_cart
            return context

        # assume logged in
        user_cart = self.request.user.cart
        if session_cart:
            if user_cart:
                user_cart.merge_another(session_cart)
                context["cart"] = user_cart
                return context
            else:
                session_cart.user = self.request.user
                session_cart.session = None
                session_cart.save()

        context["cart"] = session_cart
        return context
