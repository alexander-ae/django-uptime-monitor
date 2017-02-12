from django.conf.urls import url, include

from django.views.generic.base import TemplateView
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),

    # APPS
    url(r'', include('auth.urls')),
    url(r'^', include('uptime.urls')),

    # API
    url(r'^api/', include('api.urls', namespace='api')),

    # EXTRAS
    url(r'^humans\.txt$', TemplateView.as_view(template_name='extra/humans.txt', content_type='text/plain')),
]
