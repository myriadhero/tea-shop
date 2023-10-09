from typing import Self

from cart.models import Cart
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from products.models import Product

from .forms import OrderDetailsForm

User = get_user_model()


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "CR", _("Created")
        PENDING = "PE", _("Pending")
        SUCCESS = "SU", _("Success")
        CANCELED = "CA", _("Cancelled")

    payment_intent_id = models.CharField(max_length=100, unique=True)
    payment_intent_client_secret = models.CharField(max_length=100)
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
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(blank=True)
    cart = models.OneToOneField(
        "FrozenCart",
        on_delete=models.PROTECT,
        help_text="The exact items customer is paying for, frozen in time, so records exist even if products get removed from site.",
    )
    live_cart = models.OneToOneField(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Customer's live cart that will get deleted/emptied when order is successful.",
    )

    class Meta:
        constraints = [
            # check that when status is not Created/Canceled email is set
            models.CheckConstraint(
                # TODO: is there a way to access enum from here? instead of using "CR"?
                check=models.Q(payment_status__in=("CR", "CA"))
                | models.Q(email__isnull=False),
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
    name = models.CharField(max_length=100)
    order = models.OneToOneField(Order, blank=True, null=True, on_delete=models.CASCADE)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255)
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
            "name": self.name,
            "line1": self.line1,
            "line2": self.line2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
        }

    @classmethod
    def create_from_form(
        cls, form: OrderDetailsForm, order_or_user: Order | User
    ) -> Self:
        new_address = cls(
            name=form.cleaned_data["name"],
            line1=form.cleaned_data["line1"],
            line2=form.cleaned_data["line2"],
            city=form.cleaned_data["city"],
            state=form.cleaned_data["state"],
            postal_code=form.cleaned_data["postal_code"],
            country=form.cleaned_data["country"],
        )
        if isinstance(order_or_user, Order):
            new_address.order = order_or_user
        else:
            new_address.user = order_or_user
        new_address.save()
        return new_address

    def update_from_form(self, form: OrderDetailsForm) -> None:
        self.name = form.cleaned_data["name"]
        self.line1 = form.cleaned_data["line1"]
        self.line2 = form.cleaned_data["line2"]
        self.city = form.cleaned_data["city"]
        self.state = form.cleaned_data["state"]
        self.postal_code = form.cleaned_data["postal_code"]
        self.country = form.cleaned_data["country"]
        self.save()


class FrozenCart(models.Model):
    # TODO: can this be database computed?
    total_price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency="AUD",
        default=Money(0, "AUD"),
    )
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def create_from_cart(cls, cart: Cart) -> Self:
        frozen_cart = cls.objects.create()
        for cart_item in cart.cartitem_set.all():
            frozen_cart_item = FrozenCartItem.objects.create(
                frozen_cart=frozen_cart,
                quantity=cart_item.quantity,
                product=cart_item.product,
                name=cart_item.product.name,
                description=cart_item.product.description,
                price=cart_item.product.price,
            )
            frozen_cart.total_price += (
                frozen_cart_item.price * frozen_cart_item.quantity
            )
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
