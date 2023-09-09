from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import models, transaction
from products.models import Product

User = get_user_model()


# TODO: when a user is auth'ed,
# - if they have session cart
#  -- if no user cart - convert session cart to user cart
#  -- if they have user cart - merge and remove session cart


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

    @transaction.atomic
    def get_merged_cart(self, another_cart):
        if not another_cart:
            return self
        
        for another_cart_item in self.cart_item_set.all():
            if user_cart_item := self.cart_item_set.filter(
                product=another_cart_item.product
            ).first():
                user_cart_item.quantity += another_cart_item.quantity
                user_cart_item.save()
            else:
                another_cart_item.cart = self
                another_cart_item.save()

        another_cart.delete()
        return self


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
