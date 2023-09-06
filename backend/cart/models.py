from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import models
from products.models import Product

User = get_user_model()


class Cart(models.Model):
    session = models.OneToOneField(
        Session, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__is_null=True, session__is_null=False)
                    | models.Q(user__is_null=False, session__is_null=True)
                ),
                name="user_xor_session",
                violation_error_message="A cart must belong to either a user or an anonymous session but never nothing and never both.",
            )
        ]

    # TODO: when a user is auth'ed,
    # - if they have session cart
    #  -- and if they have user cart already, add session cart to user cart?
    # when the user is logged out, do we want to show empty cart?
    # i guess i could just have 2 carts in a scenario where user keeps 
    # logging in and out
    # and prioritise the user cart 


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
