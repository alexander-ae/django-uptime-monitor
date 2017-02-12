# -*- coding: utf-8 -*-

import logging

log = logging.getLogger('uptime')


def timedelta_milliseconds(td):
    '''
    Retorna el número de milisegundos contenido en el objeto 'timedelta' dado.
    '''
    log.debug('::timedelta_milliseconds::')
    return (td.days * 86400000 + td.seconds * 1000 + td.microseconds / 1000)
