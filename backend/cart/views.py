from django.views.generic import TemplateView


class CartPageView(TemplateView):
    template_name = "cart/cart_page.html"
