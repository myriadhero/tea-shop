from typing import Optional, Self

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.http import HttpRequest
from products.models import Product

User = get_user_model()


class SessionCart:
    pass


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def add_product(
        self, product: Product, quantity: int = 1, set_quantity: bool = False
    ) -> None:
        existing_cart_item = self.cartitem_set.filter(product=product).first()
        if existing_cart_item:
            existing_cart_item.quantity = (
                quantity if set_quantity else existing_cart_item.quantity + quantity
            )
            existing_cart_item.save()
        else:
            CartItem.objects.create(cart=self, product=product, quantity=quantity)

    @transaction.atomic
    def merge_another(self, another_cart) -> Self:
        if not another_cart:
            return self

        for another_cart_item in another_cart.cartitem_set.all():
            if user_cart_item := self.cartitem_set.filter(
                product=another_cart_item.product
            ).first():
                user_cart_item.quantity += another_cart_item.quantity
                user_cart_item.save()
            else:
                another_cart_item.cart = self
                another_cart_item.save()

        another_cart.delete()
        return self

    def __str__(self) -> str:
        return f"{self.session or self.user} Cart"

    @staticmethod
    def get_request_cart(request: HttpRequest) -> Optional[Self]:
        # session/cart items are added/created on POST
        # user may or may not have session or be logged in
        session_cart_id = request.session.get("cart_id")
        session_cart = None
        if session_cart_id:
            session_cart = Cart.objects.filter(pk=session_cart_id).first()

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
            request.session.pop("cart_id", None)

        return user_cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="One unique product per cart",
                violation_error_message="There can't be more than one of the same product in a cart, add quantity instead.",
            )
        ]

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.delete()
        else:
            return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.cart} Item: {self.product}, {self.quantity}"
