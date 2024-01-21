# Generated by Django 5.0 on 2024-01-04 13:01

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="layout",
            field=wagtail.fields.StreamField(
                [
                    (
                        "category_carousel",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        form_classname="title",
                                        help_text="If no heading is provided, the category's name will be used.",
                                    ),
                                ),
                                (
                                    "category",
                                    wagtail.blocks.PageChooserBlock("Category"),
                                ),
                                (
                                    "use_featured",
                                    wagtail.blocks.BooleanBlock(
                                        default=True,
                                        help_text="If checked, the featured posts will be used, else the latest posts.",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "page_carousel",
                        wagtail.blocks.StructBlock(
                            [
                                ("heading", wagtail.blocks.CharBlock()),
                                (
                                    "carousel_items",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                (
                                                    "page",
                                                    wagtail.blocks.PageChooserBlock(
                                                        help_text="If a page is selected, it will be used instead of the URL.",
                                                        required=False,
                                                    ),
                                                ),
                                                (
                                                    "image",
                                                    wagtail.images.blocks.ImageChooserBlock(
                                                        help_text="If no image is selected, the page's preview image will be used.",
                                                        required=False,
                                                    ),
                                                ),
                                                (
                                                    "title",
                                                    wagtail.blocks.CharBlock(
                                                        help_text="If no title is provided, the page's title will be used.",
                                                        required=False,
                                                    ),
                                                ),
                                                (
                                                    "text",
                                                    wagtail.blocks.TextBlock(
                                                        help_text="If no text is provided, the page's excerpt will be used.",
                                                        required=False,
                                                    ),
                                                ),
                                                (
                                                    "url",
                                                    wagtail.blocks.URLBlock(
                                                        help_text="If page is selected, this will be ignored.",
                                                        required=False,
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
    ]