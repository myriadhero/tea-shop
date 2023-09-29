from typing import Any, Optional, Self

from cart.models import Cart
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from products.models import Product

User = get_user_model()


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        SUCCESS = "S", _("Success")
        CANCELED = "C", _("Canceled")

    payment_intent = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.PENDING,
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

    @staticmethod
    def create_from_cart(cart: Cart, payment_intent, user=None) -> Optional[Self]:
        order = Order.objects.create()


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    order = models.OneToOneField(Order, blank=True, null=True, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    country = models.CharField(max_length=255)


class FrozenCartItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
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
