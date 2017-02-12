# -*- coding: utf-8 -*-

import json
from collections import defaultdict
from datetime import timedelta

from django.db.models import Max
from django.http import HttpResponse
from django.utils.timezone import now
from uptime.models import Evento

DAY_FORMAT = '%Y-%m-%d %H:%M %z'
UP_TRUE = 't'
UP_DOWN = 'f'


def eventos_del_ultimo_dia(request):
    """ Recupera los eventos del último día """

    dia_anterior = now() - timedelta(days=1)

    eventos = Evento.objects.filter(date_time__gt=dia_anterior).values_list(
        'site__id', 'date_time', 'up', 'last_event').order_by('site', 'date_time')

    data = defaultdict(list)

    for e in eventos:
        evento_info = {
            'date_time': e[1].strftime(DAY_FORMAT),
            'up': UP_TRUE if e[2] else UP_DOWN,
            'last_event': int(e[3])
        }

        data[e[0]].append(evento_info)

    return HttpResponse(json.dumps(data), content_type='application/json')


def ultimos_eventos_por_site(request):
    """ Recupera el listado de los últimos eventos de cada site """

    lista_eventos = Evento.objects.filter(
        id__in=Evento.objects.values('site_id').annotate(latest=Max('id')
                                                         ).values_list('latest', flat=True)).values_list('site_id',
                                                                                                         'up')

    data = []

    for evento in lista_eventos:
        evento_sitio = {
            'site': evento[0],
            'estado': UP_TRUE if evento[1] else UP_DOWN,
        }
        data.append(evento_sitio)

    return HttpResponse(json.dumps(data), content_type='application/json')
