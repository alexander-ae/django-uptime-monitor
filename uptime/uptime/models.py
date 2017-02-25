# -*- coding: utf-8 -*-

import logging

from django.contrib.auth.models import User
from django.db import models

from uuslug import uuslug

from . import choices
from .util import cancel_all_jobs, start_all_jobs

log = logging.getLogger('uptime')


class Site(models.Model):
    """ Representa a un sitio web a monitorizar. """

    active = models.BooleanField(verbose_name=u'Activo', default=True)
    name = models.CharField(verbose_name='Nombre', max_length=120, unique=True)
    slug = models.CharField(max_length=200, blank=True)
    url = models.CharField(verbose_name='URL', max_length=120, unique=True,
                           help_text='No olvide incluir el prefijo http o https según corresponda')
    timeout = models.IntegerField(verbose_name=u'Timeout', default=1000,
                                  help_text=u'Tiempo de espera máximo en milisegundos.')

    class Meta:
        verbose_name = u'Sitio web'
        verbose_name_plural = u'Sitios web'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super(Site, self).save(*args, **kwargs)

        # cancelamos y reescaneamos todos los trabajos
        cancel_all_jobs()
        start_all_jobs()

    def get_datetime_last_ping(self):
        """ Retorna la fecha/hora del último Ping  """
        try:
            return Ping.objects.filter(site=self).latest('date_time').date_time
        except:
            return None

    def get_last_event(self):
        """ Retorna el último evento """
        try:
            last_event = Evento.objects.filter(site=self).latest('date_time')
        except Evento.DoesNotExist:
            return None

        return last_event


class Ping(models.Model):
    """ Punto de verificación de estado de un sitio web. """

    site = models.ForeignKey(Site, related_name='pings')
    date_time = models.DateTimeField(verbose_name=u'Fecha/Hora',
                                     auto_now_add=True)
    up = models.BooleanField(verbose_name=u'¿Sitio activo?', default=False)
    status_code = models.CharField(verbose_name=u'Status Code', max_length=4,
                                   default='0')
    elapsed_time = models.FloatField(verbose_name=u'Tiempo transcurrido',
                                     help_text='Tiempo transcurrido desde la petición original '
                                               'en milisegundos', null=True)
    mensaje = models.CharField(verbose_name=u'Log', max_length=120, blank=True)

    class Meta:
        verbose_name = u'Estado (ping)'
        verbose_name_plural = u'Estados'

    def __str__(self):
        return self.site.__str__()


class Evento(models.Model):
    """
    Representa un cambio de estado en una web.
    Por ejemplo: cambio de estado de activo a inactivo.
    """

    site = models.ForeignKey(Site, related_name='eventos')
    date_time = models.DateTimeField(verbose_name=u'Fecha/Hora')
    up = models.BooleanField(verbose_name=u'¿Sitio activo?', default=False)
    last_event = models.CharField(verbose_name=u'Estado anterior',
                                  max_length=1, choices=choices.SITE_STATUS, default='0')

    class Meta:
        verbose_name = u'Evento'
        verbose_name_plural = u'Eventos'

    def __str__(self):
        return self.site.__str__()


# Usuario
class UsuarioPerfil(models.Model):
    """
    Perfil del usuario

    Se admiten 3 estados para la configuración de alertas:

        1. Siempre activas
        2. Apagadas
        3. Personalizadas: depende de la configuración de cada website.
    """

    user = models.OneToOneField(User, related_name='perfil')
    alertas_activas = models.CharField('Alertas Activas', choices=choices.ALERTAS_CONFIG,
                                       help_text='Configuración global', max_length=10, default='on')


class UsuarioWebsite(models.Model):
    """ Relación Usuario - Website """

    usuario = models.ForeignKey(User, related_name='websites_usuario')
    site = models.ForeignKey(Site, related_name='usuarios_website')
    alerta_email = models.BooleanField('Alerta x Email', blank=True, default=True)

    class Meta:
        unique_together = ('usuario', 'site')
