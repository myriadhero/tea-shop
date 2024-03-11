from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from pages.models import HomePage
from taggit.models import ItemBase, TagBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable, Page


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
    parent_page_types = (HomePage, "Category")

    body = StreamField(
        [
            ("rich_text", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = (
        *Page.content_panels,
        FieldPanel("body"),
        InlinePanel("featured", label="Featured Posts"),
    )


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

    content_panels = (
        *Page.content_panels,
        FieldPanel("body"),
    )

    promote_panels = (
        Page.promote_panels,
        FieldPanel("tags"),
    )

    parent_page_types = (Category,)


class FeaturedPost(Orderable):
    category = ParentalKey(Category, on_delete=models.CASCADE, related_name="featured")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="+")
    preview_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This image can be different from any images in the post.",
    )
    panels = (
        FieldPanel("post"),
        FieldPanel("preview_image"),
    )
