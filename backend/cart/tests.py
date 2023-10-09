from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse
from djmoney.money import Money
from products.models import Category, Product, ProductType

from .models import Cart, CartItem
from .views import CartPageView

User = get_user_model()
UNAME = "doggoteamaster"
UEMAIL = "dtm@alldoggos.com"
UPWORD = "randomPw@rd12!"


class CartPageTests(TestCase):
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

        self.url = reverse("cart_page")
        self.response = self.client.get(self.url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_cart_template(self):
        self.assertTemplateUsed(self.response, "cart/cart_page.html")
        self.assertContains(self.response, "treats??")
        self.assertNotContains(self.response, "Cats")

    def test_cart_url_resolves_cartpageview(self):
        view = resolve("/shop/cart/")
        self.assertEqual(view.func.view_class, CartPageView)

    def test_session_cart(self):
        # test empty cart
        self.assertContains(self.response, "No items in cart 🛒")
        # test add to cart
        self.client.post(self.url, {"product_slug": "best-oolong"})
        cart_id = self.client.session.get("cart_id", None)
        self.assertIsNotNone(cart_id)
        cart: Cart = Cart.objects.get(pk=cart_id)
        self.assertTrue(cart.cartitem_set.exists())
        self.assertEqual(cart.cartitem_set.first().product.name, "The best oolong tea")

        self.client.post(self.url, {"product_slug": "best-oolong"})
        self.assertEqual(cart.cartitem_set.first().quantity, 2)

        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "set_quantity": True, "quantity": 15},
        )
        self.assertEqual(cart.cartitem_set.first().quantity, 15)

        self.client.post(
            self.url,
            {
                "product_slug": "golden-sultan-turban",
                "set_quantity": True,
                "quantity": 33,
            },
        )
        self.assertTrue(
            cart.cartitem_set.filter(product__slug="golden-sultan-turban").exists()
        )
        self.assertEqual(cart.cartitem_set.count(), 2)

        response = self.client.get(self.url)
        self.assertContains(response, "The best oolong tea")
        self.assertContains(response, "15")
        self.assertContains(response, "Golden Sultan Turban")
        self.assertContains(response, "33")
        self.assertNotContains(response, self.product2.name)

        # test setting invalid number
        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "set_quantity": True, "quantity": 0},
        )
        self.assertEqual(cart.cartitem_set.count(), 2)
        self.assertEqual(
            cart.cartitem_set.filter(product__slug="best-oolong").first().quantity,
            15,
        )
        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "set_quantity": True, "quantity": -300},
        )
        self.assertEqual(cart.cartitem_set.count(), 2)
        self.assertEqual(
            cart.cartitem_set.filter(product__slug="best-oolong").first().quantity,
            15,
        )

        # test removing items
        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "remove_from_cart": True},
        )
        self.assertEqual(cart.cartitem_set.count(), 1)
        self.assertTrue(
            cart.cartitem_set.filter(product__slug="golden-sultan-turban").exists()
        )
        self.assertFalse(CartItem.objects.filter(product__slug="best-oolong").exists())
        self.client.post(
            self.url,
            {
                "product_slug": "golden-sultan-turban",
                "set_quantity": True,
                "quantity": 12,
                "remove_from_cart": True,
            },
        )
        self.assertFalse(Cart.objects.exists())
        self.assertFalse(CartItem.objects.exists())
        self.assertContains(self.client.get(self.url), "No items in cart 🛒")

    def test_user_cart(self):
        self.assertContains(self.response, "No items in cart 🛒")
        self.client.login(username=UNAME, password=UPWORD)
        # test empty cart
        self.assertContains(self.client.get(self.url), "No items in cart 🛒")
        # test add to cart
        self.client.post(self.url, {"product_slug": "best-oolong"})
        cart_id = self.client.session.get("cart_id", None)
        self.assertIsNone(cart_id)

        cart: Cart = self.user.cart
        self.assertTrue(cart.cartitem_set.exists())
        self.assertEqual(cart.cartitem_set.first().product.name, "The best oolong tea")

        self.client.post(self.url, {"product_slug": "best-oolong"})
        self.assertEqual(cart.cartitem_set.first().quantity, 2)

        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "set_quantity": True, "quantity": 15},
        )
        self.assertEqual(cart.cartitem_set.first().quantity, 15)

        self.client.post(
            self.url,
            {
                "product_slug": "golden-sultan-turban",
                "set_quantity": True,
                "quantity": 33,
            },
        )
        self.assertTrue(
            cart.cartitem_set.filter(product__slug="golden-sultan-turban").exists()
        )
        self.assertEqual(cart.cartitem_set.count(), 2)

        response = self.client.get(self.url)
        self.assertContains(response, "The best oolong tea")
        self.assertContains(response, "15")
        self.assertContains(response, "Golden Sultan Turban")
        self.assertContains(response, "33")
        self.assertNotContains(response, self.product2.name)

        # test cart appears empty when logging out
        self.client.logout()
        self.assertContains(self.client.get(self.url), "No items in cart 🛒")

        # test that the cart is persistent when logging back in
        self.client.login(username=UNAME, password=UPWORD)

        # test setting invalid number
        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "set_quantity": True, "quantity": 0},
        )
        self.assertEqual(cart.cartitem_set.count(), 2)
        self.assertEqual(
            cart.cartitem_set.filter(product__slug="best-oolong").first().quantity,
            15,
        )
        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "set_quantity": True, "quantity": -300},
        )
        self.assertEqual(cart.cartitem_set.count(), 2)
        self.assertEqual(
            cart.cartitem_set.filter(product__slug="best-oolong").first().quantity,
            15,
        )

        # test removing items
        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "remove_from_cart": True},
        )
        self.assertEqual(cart.cartitem_set.count(), 1)
        self.assertTrue(
            cart.cartitem_set.filter(product__slug="golden-sultan-turban").exists()
        )
        self.assertFalse(CartItem.objects.filter(product__slug="best-oolong").exists())
        self.client.post(
            self.url,
            {
                "product_slug": "golden-sultan-turban",
                "set_quantity": True,
                "quantity": 12,
                "remove_from_cart": True,
            },
        )
        self.assertFalse(Cart.objects.exists())
        self.assertFalse(CartItem.objects.exists())
        self.assertContains(self.client.get(self.url), "No items in cart 🛒")

    def test_session_to_user_merge_cart(self):
        # test add to cart
        self.client.post(
            self.url,
            {"product_slug": "best-oolong", "set_quantity": True, "quantity": 15},
        )
        self.client.post(
            self.url,
            {
                "product_slug": "golden-sultan-turban",
                "set_quantity": True,
                "quantity": 33,
            },
        )

        cart_id = self.client.session.get("cart_id", None)
        cart: Cart = Cart.objects.get(pk=cart_id)

        self.client.login(username=UNAME, password=UPWORD)
        response = self.client.get(self.url)

        self.assertEqual(cart, self.user.cart)
        self.assertIsNone(self.client.session.get("cart_id", None))
        self.assertEqual(cart.cartitem_set.count(), 2)

        self.assertContains(response, "The best oolong tea")
        self.assertContains(response, "15")
        self.assertContains(response, "Golden Sultan Turban")
        self.assertContains(response, "33")
        self.assertNotContains(response, self.product2.name)

        # test merge to filled user cart
        self.client.logout()
        self.client.post(
            self.url,
            {"product_slug": "best-oolong"},
        )
        self.client.post(
            self.url,
            {"product_slug": "not-best-oolong", "set_quantity": True, "quantity": 9},
        )
        response = self.client.get(self.url)
        self.assertContains(response, "The best oolong tea")
        self.assertContains(response, "1")
        self.assertContains(response, "Inferior oolong tea")
        self.assertContains(response, "9")

        self.client.login(username=UNAME, password=UPWORD)
        response = self.client.get(self.url)

        self.assertContains(response, "The best oolong tea")
        self.assertContains(response, "16")
        self.assertContains(response, "Inferior oolong tea")
        self.assertContains(response, "9")
        self.assertContains(response, "Golden Sultan Turban")
        self.assertContains(response, "33")

        self.assertEqual(Cart.objects.count(), 1)

    def test_out_of_stock(self):
        raise NotImplementedError
