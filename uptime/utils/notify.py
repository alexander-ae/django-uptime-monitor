# -*- coding: utf-8 -*-
import logging

from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.core.mail import EmailMessage

from premailer import transform
from redis import StrictRedis
import django_rq

log = logging.getLogger('uptime')
r = StrictRedis(**settings.REDIS_CONF)

ERRORES_CONSECUTIVOS_PARA_NOTIFICAR = settings.UPTIME_ERRORES_CONSECUTIVOS_PARA_NOTIFICAR
REDIS_EXPIRE = settings.UPTIME_REDIS_EXPIRE


def notifica(site_id, ping_id):
    """ Tarea que decide a quién notificar """

    from uptime.models import Ping, Site, UsuarioPerfil
    site = Site.objects.get(id=site_id)
    ping = Ping.objects.get(id=ping_id)

    prefix = '{0}_{1}'.format(settings.UPTIME_REDIS_PREFIX, site_id)

    usuarios_globales = UsuarioPerfil.objects.filter(alertas_activas='on').values_list('user__email', flat=True)
    usuarios_personalizados = site.usuarios_website.filter(usuario__perfil__alertas_activas='maybe', alerta_email=True
                                                           ).values_list('usuario__email', flat=True)
    usuarios_a_notificar = set(list(usuarios_globales) + list(usuarios_personalizados))

    num_errores = r.incr(prefix)

    if num_errores >= ERRORES_CONSECUTIVOS_PARA_NOTIFICAR:
        django_rq.enqueue(send_email, user_emails=usuarios_a_notificar, site=site, ping=ping)
        r.set(prefix, 0)
    else:
        r.expire(prefix, REDIS_EXPIRE)


def send_email(user_emails, site, ping):
    """ Envia una notificación por email """

    log.info('::send_email::')
    htmly = get_template('email/site-down.html')

    d = Context({
        'site': site.name,
        'ping': ping
    })

    html_content = htmly.render(d)
    email_html_content = transform(html_content)

    asunto = u'El sitio se ha caido'
    mail = 'Uptime Monitor<{0}>'.format(settings.DEFAULT_FROM_EMAIL)

    # recipients list
    if settings.UPTIME_ADMIN_EMAIL:
        log.debug('UPTIME_ADMIN_EMAIL')
        to = [settings.UPTIME_ADMIN_EMAIL]
        cc = user_emails
    else:
        log.debug('NO UPTIME_ADMIN_EMAIL')
        to = user_emails
        cc = []

    msg = EmailMessage(asunto, email_html_content, mail, to, cc)
    msg.content_subtype = "html"
    msg.send()
