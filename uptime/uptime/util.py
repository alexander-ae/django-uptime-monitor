# -*- coding: utf-8 -*-

from datetime import timedelta
from django.conf import settings
from django.db.models import Max
from django.utils.timezone import now

import django_rq

from utils.check_uptime import check_uptime

scheduler = django_rq.get_scheduler('default')

TIEMPO_ENTRE_CHECKS = settings.UPTIME_TIEMPO_ENTRE_CHECKS
TASK_DELETE_OLD_ID = 'delete_old'


def cancel_all_jobs():
    """ Cancela todos los trabajos. """
    for job in scheduler.get_jobs():
        scheduler.cancel(job)


def get_all_jobs():
    """ Lista todos los trabajos. """
    return scheduler.get_jobs()


def start_all_jobs():
    """
    Inicia los checkeos cada "TIEMPO_ENTRE_CHECKS".

    Note que en "check_uptime.check_uptime" hay un verificador que comprueba
    que los checkeos no se den dentro de un intervalo menor a cierto número de
    minutos.
    """

    from .models import Site
    sites = Site.objects.filter(active=True)
    scheduler = django_rq.get_scheduler('default')

    for site in sites:
        scheduler.schedule(now(), check_uptime, args=(site.slug,), repeat=None, interval=TIEMPO_ENTRE_CHECKS)


def get_ultimos_eventos(lista_id, up=None):
    """
    Obtiene el listado de los últimos eventos para la lista de ID's de los websites indicados.
    """

    from .models import Evento

    todos = Evento.objects.filter(
        id__in=Evento.objects.filter(site_id__in=lista_id).values('site_id').annotate(
            latest=Max('id')).values_list('latest', flat=True))

    if type(up) == bool:
        return todos.filter(up=up)
    else:
        return todos


def ultimos_eventos_dict(lista_id):
    """
    Obtiene el listado de los últimos eventos para la lista de ID's de los
    websites dados como un diccionario.
    """

    if not lista_id:
        return []

    lista_ultimos_eventos = get_ultimos_eventos(lista_id)
    ultimos = lista_ultimos_eventos.values_list('site_id', 'up')

    data = {}

    for evento in ultimos:
        data[int(evento[0])] = evento[1]

    return data


def filter_by_status(sites_list, status):
    """
    Filtra la lista de objetos Site en base al parámetro status que corresponde
    al estado del último evento registrado del sitio.
    """

    sites_list_id = sites_list.values_list('id', flat=True)

    if status == '0':
        sites_down = get_ultimos_eventos(sites_list_id, False).values_list(
            'site__id', flat=True)
        sites_list = sites_list.filter(id__in=sites_down)
    elif status == '1':
        sites_up = get_ultimos_eventos(sites_list_id, True).values_list(
            'site__id', flat=True)
        sites_list = sites_list.filter(id__in=sites_up)
    elif status == 'no-info':
        all_sites_events = get_ultimos_eventos(sites_list_id).values_list('site__id', flat=True)
        sites_list = sites_list.exclude(id__in=all_sites_events)

    return sites_list


def delete_old():
    """
    Elimina registros antiguos
    """
    from .models import Evento
    from .models import Ping

    time_limit = now() - timedelta(seconds=settings.UPTIME_TIEMPO_DE_EXPIRACION_DE_ESTADOS_Y_EVENTOS)

    Evento.objects.filter(date_time__lte=time_limit).delete()
    Ping.objects.filter(date_time__lte=time_limit).delete()


if TASK_DELETE_OLD_ID in scheduler:
    scheduler.cancel(TASK_DELETE_OLD_ID)

scheduler.schedule(now(), delete_old, repeat=True, interval=TIEMPO_ENTRE_CHECKS, id=TASK_DELETE_OLD_ID)
