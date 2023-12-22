from django import template
from wagtail.models import Page

register = template.Library()


@register.simple_tag
def get_wagtail_in_menu_items():
    # TODO: this currently returns all pages in a flat list, but it should maybe return a nested list for multitiered menus
    return Page.objects.live().in_menu()
