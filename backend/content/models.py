from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from pages.models import HomePage
from taggit.models import ItemBase, TagBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class ContentTag(TagBase):
    description = models.CharField(
        max_length=250,
        blank=True,
        help_text="250 characters long, can also be used in SEO description for the page",
    )


class TaggedWithContentTags(ItemBase):
    tag = models.ForeignKey(
        ContentTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_tags",
    )
    content_object = ParentalKey(
        to="content.Post",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class Category(Page):
    parent_page_types = [HomePage, "Category"]


class Post(Page):
    tags = ClusterTaggableManager(through=TaggedWithContentTags, blank=True)
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("rich_text", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        # block_counts={
        #     "heading": {"min_num": 1},
        #     "image": {"max_num": 5},
        # },
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("tags"),
    ]

    parent_page_types = [Category]
