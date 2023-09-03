from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    slug = models.SlugField(unique=True, help_text="Must be unique.")


class ProductType(models.Model):
    name = models.CharField(
        max_length=150,
        help_text="General Product Type, eg. tea, teaware, scarves (lol) etc.",
    )
    description = models.TextField()
    slug = models.SlugField(unique=True, help_text="Must be unique.")


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    is_published = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField()
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,
        help_text="General Product Type, eg. tea, teaware, scarves (lol) etc.",
    )
    categories = models.ManyToManyField(Category)
    slug = models.SlugField(unique=True, help_text="Must be unique.")

    def get_absolute_url(self):
        return reverse(
            "product",
            kwargs={"product_type": self.product_type.slug, "slug": self.slug},
        )
