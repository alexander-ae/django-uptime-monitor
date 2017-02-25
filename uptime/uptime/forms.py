# -*- coding: utf-8 -*-
import logging

from django import forms

from .models import Site, UsuarioWebsite, UsuarioPerfil
from . import choices

log = logging.getLogger('uptime')


class SiteForm(forms.Form):
    """ Formulario de registro de un nuevo Site """

    active = forms.BooleanField(label=u'Activo', required=False, initial=True)
    name = forms.CharField(label='Nombre', max_length=120)
    url = forms.URLField(label='URL', max_length=120,
                         help_text='No olvide incluir el prefijo http o https según corresponda')
    url.widget.attrs.update({'placeholder': 'https://www.python.org/'})
    timeout = forms.IntegerField(label=u'Timeout', initial=1000, help_text=u'Tiempo de espera máximo en milisegundos.')

    def clean_name(self):
        """ Verifica que el nombre no haya sido registrado. """
        name = self.cleaned_data['name']
        sites_exist = Site.objects.filter(name=name).exists()

        if sites_exist:
            raise forms.ValidationError('Ya existe un sitio con el mismo nombre')

        return name

    def clean_url(self):
        """ Verifica que la url no haya sido registrada. """
        url = self.cleaned_data['url']
        sites_exist = Site.objects.filter(url=url).exists()

        if sites_exist:
            raise forms.ValidationError('Ya existe un sitio con la misma URL')

        return url

    def save(self):
        cd = self.cleaned_data
        Site(**cd).save()


class SiteEditForm(forms.Form):
    """ Formulario de edición de un nuevo Site """

    slug = forms.CharField(label='slug', max_length=200, widget=forms.HiddenInput())
    active = forms.BooleanField(label=u'Activo', required=False)
    name = forms.CharField(label='Nombre', max_length=120)
    url = forms.URLField(label='URL', max_length=120,
                         help_text='No olvide incluir el prefijo http o https según corresponda')
    timeout = forms.IntegerField(label=u'Timeout',
                                 help_text=u'Tiempo de espera máximo en milisegundos.')

    def clean(self):
        slug = self.cleaned_data['slug']
        name = self.cleaned_data['name']
        url = self.cleaned_data.get('url')

        # name
        name_exist = Site.objects.filter(name=name).exclude(slug=slug).exists()

        if name_exist:
            raise forms.ValidationError('Ya existe un sitio con el mismo nombre')

        # url
        if not url:
            raise forms.ValidationError(u'URL inválida')

        url_exist = Site.objects.filter(url=url).exclude(slug=slug).exists()

        if url_exist:
            raise forms.ValidationError('Ya existe un sitio con la misma URL')

        return self.cleaned_data

    def update(self):
        cd = self.cleaned_data
        sites = Site.objects.filter(slug=cd['slug'])
        sites.update(**cd)

        sites[0].save()


class UsuarioWebsiteForm(forms.Form):
    """ Formulario de (des)activación de alertas por email """

    alerta_email = forms.BooleanField(label=u'Notificaciones por email', required=False)

    def save(self, usuario, site):
        alerta_email = self.cleaned_data.get('alerta_email', False)

        usuarioWebsite = UsuarioWebsite.objects.get(usuario=usuario, site=site)
        usuarioWebsite.alerta_email = alerta_email
        usuarioWebsite.save()


class ConfigAlertasForm(forms.Form):
    """ Formulario de configuración global de las alertas  """

    alertas = forms.ChoiceField(label='Alertas Activas', choices=choices.ALERTAS_CONFIG,
                                initial='on')

    def save(self, usuario):
        cd = self.cleaned_data
        usuarioPerfil = UsuarioPerfil.objects.get(user=usuario)
        usuarioPerfil.alertas_activas = cd['alertas']
        usuarioPerfil.save()
