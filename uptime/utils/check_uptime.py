# -*- coding: utf-8 -*-

from datetime import timedelta
import logging

from django.conf import settings
from django.utils.timezone import now

import requests
from requests.exceptions import (ConnectionError, HTTPError, URLRequired,
                                 TooManyRedirects, Timeout)
import django_rq

from .utils import timedelta_milliseconds
from .notify import notifica

log = logging.getLogger('uptime')

DEFAULT_ELAPSED_TIME = settings.UPTIME_DEFAULT_ELAPSED_TIME
TIEMPO_MINIMO_ENTRE_PINGS = timedelta(seconds=settings.UPTIME_TIEMPO_ENTRE_CHECKS)
TIEMPO_MINIMO_ENTRE_EVENTOS = settings.UPTIME_TIEMPO_MINIMO_ENTRE_EVENTOS
TIEMPO_MAXIMO_ULTIMO_EVENTO = settings.UPTIME_TIEMPO_MAXIMO_ULTIMO_EVENTO


def check_uptime(site_slug):
    """
    Verifica si un sitio se encuentra activo o no.
    Almacena la respuesta en un objeto 'Ping'.
    """

    log.debug('::check_uptime:: site_slug=' + site_slug)

    from uptime.models import Site, Ping

    site = Site.objects.get(slug=site_slug)

    # en caso de que las verificaciones se queden estancadas y el worker se reinicie,
    # se debe evitar generar múltiples pings seguidos
    datetime_last_ping = site.get_datetime_last_ping()
    if datetime_last_ping:
        if now() - datetime_last_ping < TIEMPO_MINIMO_ENTRE_PINGS:
            return

    # ping
    ping = Ping(site=site, elapsed_time=DEFAULT_ELAPSED_TIME)
    ping.save()
    django_rq.enqueue(ejecuta_ping, ping.id)


def ejecuta_ping(ping_id):
    """
    Verifica el estado de la página y genera un objeto Ping basado en el mismo.
    """

    log.debug('::ejecuta_ping::')
    from uptime.models import Ping

    ping = Ping.objects.get(id=ping_id)
    site = ping.site

    # consultamos la url
    try:
        if site.timeout:
            r = requests.head(site.url, timeout=site.timeout / 1000.0, allow_redirects=True)
        else:
            r = requests.head(site.url, allow_redirects=True)

        ping.status_code = r.status_code
        ping.elapsed_time = timedelta_milliseconds(r.elapsed)

        if r.status_code == requests.codes.ok:
            ping.up = True
            msg = "Todo OK"
        else:
            msg = "Error de estado"
            ping.elapsed_time = DEFAULT_ELAPSED_TIME
            log.error('Error de Estado')

        log.info('OK')
    except Timeout:
        msg = 'Timeout'
    except ConnectionError:
        msg = u'ConnectionError'
    except HTTPError:
        msg = u'HTTPError'
    except URLRequired:
        msg = u'URLRequired'
    except TooManyRedirects:
        msg = u'TooManyRedirects'
    except:
        msg = 'Error inesperado'

    ping.mensaje = msg
    ping.save()

    django_rq.enqueue(procesa_evento, ping.id)

    # en caso de error, se preparan las notificaciones
    if not ping.up:
        django_rq.enqueue(notifica, site_id=site.id, ping_id=ping.id)

    return 'OK'


def procesa_evento(ping_id):
    """
    Genera un evento si el estado del nuevo Ping difiere del último estado
    almacenado, no existen eventos o el último evento fue antes del tiempo
    indicado .
    """

    log.debug('::procesa_evento::')
    from uptime.models import Evento, Ping

    ping = Ping.objects.get(id=ping_id)
    site = ping.site
    last_event = site.get_last_event()
    ahora = now()

    if not last_event:
        Evento(site=site, date_time=ping.date_time, up=ping.up).save()
        return True

    limite_anterior = ahora - TIEMPO_MINIMO_ENTRE_EVENTOS

    # ¿el estado ha cambiado o transcurrió el tiempo minimo para registrar un nuevo evento?
    if (last_event.up != ping.up) or (last_event.date_time < limite_anterior):

        # ¿transcurrió el tiempo máximo para tener en cuenta al último evento?
        if (ahora - last_event.date_time) > TIEMPO_MAXIMO_ULTIMO_EVENTO:
            last_event_up = '0'
        elif last_event.up:
            last_event_up = '1'
        else:
            last_event_up = '2'

        # registramos el evento
        Evento(site=site, date_time=ping.date_time, up=ping.up, last_event=last_event_up).save()

    return 'OK'
