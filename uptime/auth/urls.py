from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ingresar/$', views.login_view, name='login'),
    url(r'^salir/$', views.logout, name='logout'),
]
