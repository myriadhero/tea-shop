from django.test import TestCase
from django.urls import resolve, reverse

from .models import Category, Product, ProductType
from .views import CategoryDetailView, ProductDetailView, ProductTypeDetailView


class ProductPageTests(TestCase):
    def setUp(self) -> None:
        self.ptype = ProductType.objects.create(
            name="Teas", slug="teas", description="all the teas"
        )
        self.category = Category.objects.create(
            name="Oolongs", slug="oolongs", description="all oolong teas"
        )
        self.product = Product.objects.create(
            name="The best oolong tea",
            description="Sooo fragrant",
            is_published=True,
            quantity=42,
            product_type=self.ptype,
            slug="best-oolong",
        )
        self.product.categories.add(self.category)

        self.url = reverse(
            "product_details",
            kwargs={"product_type": self.ptype.slug, "slug": self.product.slug},
        )
        self.response = self.client.get(self.url)

    def test_get_absolute_url(self):
        self.assertEqual(self.url, self.product.get_absolute_url())

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_product_detail_template(self):
        self.assertTemplateUsed(self.response, "products/product_detail.html")
        self.assertContains(self.response, self.product.description)
        self.assertNotContains(self.response, "cats")

    def test_url_resolves_productdetailview(self):
        view = resolve(self.url)
        self.assertEqual(view.func.view_class, ProductDetailView)


class CategoryPageTests(TestCase):
    def setUp(self) -> None:
        self.ptype = ProductType.objects.create(
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
            product_type=self.ptype,
            slug="best-oolong",
        )
        self.product2 = Product.objects.create(
            name="Inferior oolong tea",
            description="Only so fragrant",
            is_published=True,
            quantity=42,
            product_type=self.ptype,
            slug="not-best-oolong",
        )
        self.product1.categories.add(self.category)
        self.product2.categories.add(self.category)

        self.unrelated_product = Product.objects.create(
            name="Golden Sultan Tea",
            description="Hits different",
            is_published=True,
            quantity=42,
            product_type=self.ptype,
            slug="golden-sultan",
        )

        self.url = reverse("products_by_category", kwargs={"slug": self.category.slug})
        self.response = self.client.get(self.url)

    def test_get_absolute_url(self):
        self.assertEqual(self.url, self.category.get_absolute_url())

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_product_detail_template(self):
        self.assertTemplateUsed(self.response, "products/by_category.html")
        self.assertContains(self.response, self.category.name)
        self.assertContains(self.response, self.product1.name)
        self.assertContains(self.response, self.product2.name)
        self.assertNotContains(self.response, self.unrelated_product.name)
        self.assertNotContains(self.response, "cats")

    def test_url_resolves_productdetailview(self):
        view = resolve(self.url)
        self.assertEqual(view.func.view_class, CategoryDetailView)


class PTypePageTests(TestCase):
    def setUp(self) -> None:
        self.ptype = ProductType.objects.create(
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
            product_type=self.ptype,
            slug="best-oolong",
        )
        self.product2 = Product.objects.create(
            name="Inferior oolong tea",
            description="Only so fragrant",
            is_published=True,
            quantity=42,
            product_type=self.ptype,
            slug="not-best-oolong",
        )
        self.product1.categories.add(self.category)

        self.unrelated_type = ProductType.objects.create(
            name="Scarves", description="what is this all about??", slug="not-scarves"
        )
        self.unrelated_product = Product.objects.create(
            name="Golden Sultan Tea",
            description="Hits different",
            is_published=True,
            quantity=42,
            product_type=self.unrelated_type,
            slug="golden-sultan",
        )

        self.url = reverse("products_by_type", kwargs={"slug": self.ptype.slug})
        self.response = self.client.get(self.url)

    def test_get_absolute_url(self):
        self.assertEqual(self.url, self.ptype.get_absolute_url())

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_product_detail_template(self):
        self.assertTemplateUsed(self.response, "products/by_type.html")
        self.assertContains(self.response, self.ptype.name)
        self.assertContains(self.response, self.product1.name)
        self.assertContains(self.response, self.product2.name)
        self.assertNotContains(self.response, self.unrelated_product)
        self.assertNotContains(self.response, "cats")

    def test_url_resolves_productdetailview(self):
        view = resolve(self.url)
        self.assertEqual(view.func.view_class, ProductTypeDetailView)


class AllProductsPageTests(TestCase):
    # TODO: test this page!
    pass


class FeaturedProductsPageTests(TestCase):
    # TODO: test this page!
    pass
