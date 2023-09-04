from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .views import HomePageView


class HomePageTests(SimpleTestCase):
    def setUp(self) -> None:
        url = reverse("home")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "pages/home.html")
        self.assertContains(self.response, "Woohoo")
        self.assertNotContains(self.response, "Cats")

    def test_homepage_url_resolves_homepageview(self):  # new
        view = resolve("/")
        self.assertEqual(view.func.__name__, HomePageView.as_view().__name__)


class AboutPageTests(SimpleTestCase):
    def setUp(self) -> None:
        url = reverse("about")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "pages/about.html")
        self.assertContains(self.response, "Yes dis dog")
        self.assertNotContains(self.response, "Cats")

    def test_homepage_url_resolves_homepageview(self):  # new
        view = resolve("/about/")
        self.assertEqual(view.func.__name__, HomePageView.as_view().__name__)
