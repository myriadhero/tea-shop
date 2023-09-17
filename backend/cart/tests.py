from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse
from products.models import Category, Product, ProductType

from .models import Cart, CartItem
from .views import CartPageView

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
        )
        self.product2 = Product.objects.create(
            name="Inferior oolong tea",
            description="Only so fragrant",
            is_published=True,
            quantity=42,
            product_type=self.ptype1,
            slug="not-best-oolong",
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
        )

        self.user = get_user_model().objects.create_superuser(
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
                "quantity": 15,
            },
        )
        self.assertTrue(
            cart.cartitem_set.filter(product__slug="golden-sultan-turban").exists()
        )
        self.assertEqual(cart.cartitem_set.count(), 2)

    def test_user_cart(self):
        self.client.login(username=UNAME, password=UPWORD)
        # test empty cart
        self.assertContains(self.response, "No items in cart 🛒")
        # test add to cart
        raise NotImplementedError

    def test_session_to_user_merge_cart(self):
        # test empty cart
        # test add to cart
        raise NotImplementedError

    def test_remove_from_cart(self):
        raise NotImplementedError

    def test_out_of_stock(self):
        raise NotImplementedError
