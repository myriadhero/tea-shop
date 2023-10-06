from typing import Self

from cart.models import Cart
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from products.models import Product

User = get_user_model()


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "CR", _("Created")
        PENDING = "PE", _("Pending")
        SUCCESS = "SU", _("Success")
        CANCELED = "CA", _("Cancelled")

    payment_intent = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.CREATED,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    email = models.EmailField(blank=True)
    cart = models.OneToOneField("FrozenCart", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            # check that when status is not Created/Canceled email is set
            models.CheckConstraint(
                # TODO: is there a way to access enum from here? instead of using "CR"?
                check=~models.Q(payment_status__in=("CR", "CA"))
                & models.Q(email__isnull=False),
                name="email_required",
                violation_error_message="An order must be associated with an email.",
            )
        ]

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.user or self.email}"


class Address(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    order = models.OneToOneField(Order, blank=True, null=True, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Addresses"
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=True) ^ models.Q(order__isnull=True),
                name="user_or_order",
                violation_error_message="An address must be associated with either a user or an order, but not both.",
            )
        ]

    def to_dict(self) -> dict[str, str]:
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
        }


class FrozenCart(models.Model):
    total_price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency="AUD",
        default=Money(0, "AUD"),
    )
    created = models.DateField(auto_now_add=True)

    @classmethod
    def create_from_cart(cls, cart: Cart) -> Self:
        frozen_cart = cls()
        for cart_item in cart.cartitem_set.all():
            FrozenCartItem.objects.create(
                frozen_cart=frozen_cart,
                quantity=cart_item.quantity,
                product=cart_item.product,
                name=cart_item.name,
                description=cart_item.description,
                price=cart_item.price,
            )
            frozen_cart.total_price += cart_item.price * cart_item.quantity
        frozen_cart.save()
        return frozen_cart


class FrozenCartItem(models.Model):
    frozen_cart = models.ForeignKey(FrozenCart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency="AUD")
