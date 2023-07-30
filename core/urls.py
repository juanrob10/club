"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app imposrt views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

    """

from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _

admin.site.site_header = _("CLUB Admin")
admin.site.site_title = _("CLUB Admin Portal")
admin.site.index_title = _("Welcome to the homework club management portal")

urlpatterns = i18n_patterns(
    path('',include("school.urls")),
    path('admin/', admin.site.urls),
    # If no prefix is given, use the default language
    prefix_default_language=False,
)

if  settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


