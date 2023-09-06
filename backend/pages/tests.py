from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .views import AboutPageView, HomePageView


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

    def test_homepage_url_resolves_homepageview(self):
        view = resolve("/")
        self.assertEqual(view.func.view_class, HomePageView)


class AboutPageTests(SimpleTestCase):
    def setUp(self) -> None:
        url = reverse("about")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_aboutpage_template(self):
        self.assertTemplateUsed(self.response, "pages/about.html")
        self.assertContains(self.response, "Yes dis dog")
        self.assertNotContains(self.response, "Cats")

    def test_url_resolves_aboutpageview(self):
        view = resolve("/about/")
        self.assertEqual(view.func.view_class, AboutPageView)
