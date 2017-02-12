from django.conf.urls import url
from . import views

urlpatterns = [
    # websites
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^websites/$', views.websites, name='websites'),
    url(r'^websites/registro/$', views.website_new, name='website_new'),

    # website
    url(r'^website/(?P<slug>[-\w]+)/$', views.website, name='website'),
    url(r'^website/(?P<slug>[-\w]+)/editar/$', views.website_edit, name='website_edit'),
    url(r'^website/(?P<slug>[-\w]+)/notificaciones/$', views.website_alertas, name='website_alertas'),
    url(r'^website/(?P<slug>[-\w]+)/eliminar/$', views.website_delete, name='website_delete'),

    # extras
    url(r'^configuracion/$', views.settings, name='settings'),

    url(r'^cancel-jobs/$', views.cancel_jobs, name='cancel_all_jobs'),
    url(r'^get-all-jobs/$', views.all_jobs, name='get_all_jobs'),
]
