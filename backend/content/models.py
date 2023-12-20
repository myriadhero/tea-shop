from django.db import models
from pages.models import HomePage
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class Category(Page):
    parent_page_types = [HomePage, "Category"]


class Post(Page):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        block_counts={
            "heading": {"min_num": 1},
            "image": {"max_num": 5},
        },
        use_json_field=True,
    )

    parent_page_types = [Category]
