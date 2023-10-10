"""
URL configuration for TeaShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from orders.views import CheckoutPageView
from products.views import FeaturedProductsView

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("shop/cart/", include("cart.urls")),
    path(
        # TODO: rethink the checkout/orders urls
        "shop/checkout/",
        CheckoutPageView.as_view(),
        name="checkout",
    ),
    path("shop/orders/", include("orders.urls")),
    path("shop/", include("products.urls")),
    path("tea-of-the-month/", FeaturedProductsView.as_view(), name="featured_products"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
