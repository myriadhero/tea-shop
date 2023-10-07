from collections.abc import Iterable
from typing import Optional, Self

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.http import HttpRequest
from django.utils import timezone
from products.models import Product

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def add_product(
        self, product: Product, quantity: int = 1, set_quantity: bool = False
    ) -> None:
        # TODO: add quantity availability checks
        existing_cart_item: CartItem = self.cartitem_set.filter(product=product).first()
        if existing_cart_item:
            existing_cart_item.quantity = (
                quantity if set_quantity else existing_cart_item.quantity + quantity
            )
            existing_cart_item.save()
        else:
            CartItem.objects.create(cart=self, product=product, quantity=quantity)

    def remove_product(self, product: Product):
        existing_cart_item = self.cartitem_set.filter(product=product).first()
        if existing_cart_item:
            existing_cart_item.delete()

    @transaction.atomic
    def merge_another(self, another_cart: Self) -> Self:
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
        return f"{self.user or 'Session'+self.id} Cart"

    @staticmethod
    def get_request_cart(request: HttpRequest, create_cart=False) -> Optional[Self]:
        # session/cart items are added/created on POST
        # user may or may not have session or be logged in
        session_cart_id = request.session.get("cart_id")
        session_cart = None
        if session_cart_id:
            session_cart = Cart.objects.filter(pk=session_cart_id).first()

        if not request.user.is_authenticated:
            if not session_cart and create_cart:
                session_cart = Cart.objects.create()
                request.session["cart_id"] = session_cart.id

            return session_cart

        # assume user is authenticated from this point
        try:
            user_cart: Optional[Cart] = request.user.cart
        except User.cart.RelatedObjectDoesNotExist:
            user_cart = None

        if session_cart:
            if user_cart:
                user_cart.merge_another(session_cart)
            else:
                user_cart = session_cart
                user_cart.user = request.user
                user_cart.save()

            request.session.pop("cart_id", None)

        if not user_cart and create_cart:
            user_cart = Cart.objects.create(user=request.user)

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
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="Quantity can't be 0",
                violation_error_message="Cart item quantity can't be 0 or less, use delete instead.",
            ),
        ]

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        cart_item_id = self.id
        cart = self.cart
        delete_results = super().delete(*args, **kwargs)
        if not cart.cartitem_set.exclude(id=cart_item_id).exists():
            cart.delete()
        else:
            cart.save()
        return delete_results

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        self.cart.save()

    def __str__(self) -> str:
        return f"{self.cart} Item: {self.product}, {self.quantity}"
