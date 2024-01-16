from content.blocks import CategoryCarouselBlock, PageCarouselBlock
from django.db import models
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.blocks import RichTextBlock
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page


@register_setting
class SiteIdentity(BaseGenericSetting):
    site_title = models.CharField(max_length=100)
    title_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Used for the main top logo",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    seo_description = models.TextField(
        blank=True,
        help_text="Used in SEO meta tags, should be 50-160 characters long",
    )
    seo_keywords = models.CharField(
        max_length=250,
        blank=True,
        help_text="List of words in SEO meta tags, eg 'blog, django, python' without quotes, comma separated",
    )

    footer = StreamField(
        [
            ("rich_text", RichTextBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )
    info_popup = models.TextField(
        blank=True,
        help_text="Adds a message to the top of the site on all pages. Change to blank to remove the message.",
    )

    youtube_url = models.URLField(blank=True)
    youtube_name = models.CharField(
        max_length=100,
        blank=True,
    )
    twitter_url = models.URLField(blank=True)
    twitter_name = models.CharField(
        max_length=100,
        blank=True,
    )

    content_panels = (
        FieldPanel("site_title"),
        FieldPanel("title_logo"),
        FieldPanel("favicon"),
        FieldPanel("seo_description"),
        FieldPanel("seo_keywords"),
        FieldPanel("info_popup"),
        FieldPanel("footer"),
    )
    socials_panels = (
        FieldPanel("youtube_url"),
        FieldPanel("youtube_name"),
        FieldPanel("twitter_url"),
        FieldPanel("twitter_name"),
    )

    edit_handler = TabbedInterface(
        (
            ObjectList(content_panels, heading="Main"),
            ObjectList(socials_panels, heading="Socials"),
        ),
    )


class HomePage(Page):
    max_count = 1
    layout = StreamField(
        [
            ("category_carousel", CategoryCarouselBlock()),
            ("page_carousel", PageCarouselBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )
    parent_page_types = (Page,)
    content_panels = (
        *Page.content_panels,
        FieldPanel("layout"),
    )


class AboutPage(Page):
    max_count = 1
    parent_page_types = (HomePage,)


class FeaturedPage(Page):
    parent_page_types = (HomePage,)
