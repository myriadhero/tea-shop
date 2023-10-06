from django.db import models
from django.urls import reverse
from djmoney.models.fields import MoneyField


class Category(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    slug = models.SlugField(unique=True, help_text="Must be unique.")

    def get_absolute_url(self):
        return reverse(
            "products_by_category",
            kwargs={"slug": self.slug},
        )

    def __str__(self) -> str:
        return self.name


class ProductType(models.Model):
    name = models.CharField(
        max_length=150,
        help_text="General Product Type, eg. tea, teaware, scarves (lol) etc.",
    )
    description = models.TextField()
    slug = models.SlugField(unique=True, help_text="Must be unique.")

    def get_absolute_url(self):
        return reverse(
            "products_by_type",
            kwargs={"slug": self.slug},
        )

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    is_published = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField()
    price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency="AUD",
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,
        help_text="General Product Type, eg. tea, teaware, scarves (lol) etc.",
    )
    categories = models.ManyToManyField(Category)
    slug = models.SlugField(unique=True, help_text="Must be unique.")

    def get_absolute_url(self):
        return reverse(
            "product_details",
            kwargs={"product_type": self.product_type.slug, "slug": self.slug},
        )

    def __str__(self) -> str:
        return self.name
