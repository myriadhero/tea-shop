from django.test import TestCase
from django.urls import resolve, reverse

from .views import CartPageView


class CartPageTests(TestCase):
    def setUp(self) -> None:
        url = reverse("cart_page")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_featured_products_template(self):
        self.assertTemplateUsed(self.response, "cart/cart_page.html")
        self.assertContains(self.response, "treats??")
        self.assertNotContains(self.response, "Cats")

    def test_featured_products_url_resolves_homepageview(self):
        view = resolve("/cart/")
        self.assertEqual(view.func.view_class, CartPageView)
