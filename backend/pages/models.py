from django.db import models
from wagtail.models import Page


class HomePage(Page):
    max_count = 1
    parent_page_types = [Page]


class AboutPage(Page):
    max_count = 1
    parent_page_types = [HomePage]


class FeaturedPage(Page):
    parent_page_types = [HomePage]
