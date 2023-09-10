from typing import Any, Optional

from cart.models import Cart
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = "Remove carts that were tied to expired or deleted sessions and are no longer used"

    def handle(self, *args: Any, **options: Any) -> str | None:
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        expired_cart_ids = [
            cart_id
            for session in expired_sessions
            if (cart_id := session.get_decoded().get("cart_id"))
        ]

        expired_carts = Cart.objects.filter(id__in=expired_cart_ids)
        expired_cart_count = expired_carts.count()
        expired_carts.delete()

        # remove carts that are orphaned altogether
        session_carts_ids = set(
            Cart.objects.filter(user__isnull=True).values_list("id", flat=True)
        )

        for session in Session.objects.filter(expire_date__gt=timezone.now()):
            cart_id = session.get_decoded().get("cart_id")
            if cart_id in session_carts_ids:
                session_carts_ids.remove(cart_id)

        orphaned_carts = Cart.objects.filter(id__in=session_carts_ids)
        orphaned_cart_count = orphaned_carts.count()
        orphaned_carts.delete()

        return f"Removed {expired_cart_count} carts with expired sessions! Removed {orphaned_cart_count} completely orphaned carts! Feel free to clear expired sessions."
