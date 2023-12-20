from django.views.generic import TemplateView


# TODO: clear this file and remove the import in views.py
class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


class TeaOfTheMonthPageView(TemplateView):
    template_name = "pages/tea_of_the_month.html"
