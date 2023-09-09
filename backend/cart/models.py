from typing import Optional, Self

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import models, transaction
from django.http import HttpRequest
from products.models import Product

User = get_user_model()


# TODO: when a user is auth'ed,
# - if they have session cart
#  -- if no user cart - convert session cart to user cart
#  -- if they have user cart - merge and remove session cart


class SessionCart:
    pass


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    @transaction.atomic
    def merge_another(self, another_cart):
        if not another_cart:
            return self

        for another_cart_item in another_cart.cart_item_set.all():
            if user_cart_item := self.cart_item_set.filter(
                product=another_cart_item.product
            ).first():
                user_cart_item.quantity += another_cart_item.quantity
                user_cart_item.save()
            else:
                another_cart_item.cart = self
                another_cart_item.save()

        another_cart.delete()

    def __str__(self) -> str:
        return f"{self.session or self.user} Cart"

    @staticmethod
    def get_request_cart(request: HttpRequest) -> Optional[Self]:
        # session/cart items are added/created on POST
        # user may or may not have session or be logged in
        session_cart = None
        if request.session.session_key:
            try:
                session_cart: Optional[Cart] = Session.objects.get(
                    pk=request.session.session_key
                ).cart
            except Session.cart.RelatedObjectDoesNotExist:
                pass

        if not request.user.is_authenticated:
            return session_cart

        # assume user is authenticated from this point
        try:
            user_cart: Optional[Cart] = request.user.cart
        except User.cart.RelatedObjectDoesNotExist:
            user_cart = None

        if session_cart and not user_cart:
            user_cart = Cart.objects.create(user=request.user)
        
        if user_cart:
            user_cart.merge_another(session_cart)

        return user_cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.cart} Item: {self.product}, {self.quantity}"
