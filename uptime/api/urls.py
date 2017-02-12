from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^eventos/ultimo-dia/$', views.eventos_del_ultimo_dia, name='eventos_del_ultimo_dia'),
    url(r'^eventos/ultimos-por-site/$', views.ultimos_eventos_por_site, name='ultimos_eventos_por_site'),
]
