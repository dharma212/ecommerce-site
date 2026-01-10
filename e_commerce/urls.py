from django.contrib import admin
from django.urls import path, include
from E_commerce_site.views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("user/", include("users.urls")),
    path("product/", include("product.urls")),
    path("dashboard/",include("dashboard.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)