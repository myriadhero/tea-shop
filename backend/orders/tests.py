from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse
from djmoney.money import Money
from products.models import Category, Product, ProductType

from .models import Order
from .views import (
    CheckoutDetailsUpdateView,
    CheckoutPageView,
    OrderSuccessPageView,
    StripeWebhookView,
)

User = get_user_model()
UNAME = "doggoteanoob"
UEMAIL = "dtn@alldoggos.com"
UPWORD = "randomPw@rd12!3"


class MockPaymentIntent:
    modified_counter = 0

    def __init__(self, payment_id, amount, modified=False) -> None:
        self.id = f"test_id_{payment_id}"
        self.client_secret = f"client_secret_{payment_id}"
        self.amount = amount

    def modify(self, amount):
        self.amount = amount
        self.modified_counter += 1
        self.client_secret += f"_M{self.modified_counter}"
        return self

    def __repr__(self) -> str:
        return (
            f"MockPaymentIntent {self.id}, {self.client_secret}, amount: {self.amount}"
        )


class StripePaymentIntentMockFactory:
    id_counter = 0
    all_intents = {}

    @classmethod
    def create(cls, *args, **kwargs):
        cls.id_counter += 1
        intent_mock = MockPaymentIntent(
            payment_id=cls.id_counter,
            amount=kwargs["amount"],
        )
        cls.all_intents[intent_mock.id] = intent_mock
        return intent_mock

    @classmethod
    def modify(cls, *args, **kwargs):
        intent_mock = cls.all_intents[args[0]]
        intent_mock.modify(kwargs["amount"])

        return intent_mock


class CheckoutPageTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        patch(
            "stripe.PaymentIntent.create", StripePaymentIntentMockFactory.create
        ).start()
        patch(
            "stripe.PaymentIntent.modify", StripePaymentIntentMockFactory.modify
        ).start()

        return super().setUpClass()

    def setUp(self) -> None:
        self.ptype1 = ProductType.objects.create(
            name="Teas", slug="teas", description="all the teas"
        )
        self.category = Category.objects.create(
            name="Oolongs", slug="oolongs", description="all oolong teas"
        )
        self.product1 = Product.objects.create(
            name="The best oolong tea",
            description="Sooo fragrant",
            is_published=True,
            quantity=42,
            product_type=self.ptype1,
            slug="best-oolong",
            price=Money(5, "AUD"),
        )
        self.product2 = Product.objects.create(
            name="Inferior oolong tea",
            description="Only so fragrant",
            is_published=True,
            quantity=42,
            product_type=self.ptype1,
            slug="not-best-oolong",
            price=Money(3, "AUD"),
        )
        self.product1.categories.add(self.category)

        self.ptype2 = ProductType.objects.create(
            name="Teawares", description="What doggos use to make tea", slug="teawares"
        )
        self.product3 = Product.objects.create(
            name="Golden Sultan Turban",
            description="The best thinking hat for a doggo",
            is_published=True,
            quantity=42,
            product_type=self.ptype2,
            slug="golden-sultan-turban",
            price=Money(7, "AUD"),
        )

        self.user = User.objects.create_user(
            username=UNAME,
            email=UEMAIL,
            password=UPWORD,
        )

        self.url = reverse("checkout")
        # add item to cart to be able to checkout
        self.client.post(reverse("cart_page"), {"product_slug": self.product1.slug})
        self.response = self.client.get(self.url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

        # redirect to cart page if cart is empty
        self.client.post(
            reverse("cart_page"),
            {"product_slug": self.product1.slug, "remove_from_cart": True},
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_checkout_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "orders/checkout.html")
        self.assertContains(self.response, "prefill and save email and address")
        self.assertNotContains(self.response, "Cats")

    def test_checkout_url_resolves_checkout_view(self):
        view = resolve("/shop/checkout/")
        self.assertEqual(view.func.view_class, CheckoutPageView)

    @classmethod
    def tearDownClass(cls) -> None:
        patch.stopall()
        return super().tearDownClass()
