from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class CategoryCarouselBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        form_classname="title",
        help_text="If no heading is provided, the category's name will be used.",
        required=False,
    )
    category = blocks.PageChooserBlock("content.Category")
    use_featured = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="If checked, the featured posts will be used, else the latest posts.",
    )

    class Meta:
        icon = "image"
        label = "Category Carousel"


class PageOrUrlBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(
        required=False,
        help_text="If a page is selected, it will be used instead of the URL. Any page made in Wagtail can be chosen including categories.",
    )
    image = ImageChooserBlock(
        required=False,
        help_text="If no image is selected, the page's preview image will be used if the page has one.",
    )
    title = blocks.CharBlock(
        required=False,
        help_text="If no title is provided, the page's title will be used.",
    )
    text = blocks.TextBlock(
        required=False,
        help_text="If no text is provided, the page's excerpt will be used.",
    )
    url = blocks.URLBlock(
        required=False, help_text="If page is selected, this will be ignored."
    )

    class Meta:
        icon = "link"
        label = "Page or URL"


class PageCarouselBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    carousel_items = blocks.ListBlock(PageOrUrlBlock())

    class Meta:
        icon = "image"
        label = "Page Carousel"
