from content.blocks import CategoryCarouselBlock, PageCarouselBlock
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page


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
    parent_page_types = [Page]
    content_panels = Page.content_panels + [
        FieldPanel("layout"),
    ]


class AboutPage(Page):
    max_count = 1
    parent_page_types = [HomePage]


class FeaturedPage(Page):
    parent_page_types = [HomePage]
