# -*- coding: utf-8 -*-

import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now

from .forms import SiteForm, SiteEditForm, UsuarioWebsiteForm, ConfigAlertasForm
from .models import Site, Evento, UsuarioWebsite, UsuarioPerfil
from .util import (cancel_all_jobs, get_all_jobs, ultimos_eventos_dict, filter_by_status)

log = logging.getLogger('uptime')


@login_required
def dashboard(request):
    """ Vista inicial (resumen) """

    sites = Site.objects.all()[:15]
    ultimos_eventos = Evento.objects.all().order_by('-id')[:10].values_list(
        'up', 'site__name', 'date_time', 'site__slug')

    return render(request, 'dashboard.html', locals())


@login_required
def websites(request):
    """ Listado de los Sitios registrados """

    user = request.user

    sites_list = Site.objects.all()
    SITES_PER_PAGE = 20

    # filtro por estado
    status = request.GET.get('s')
    sites_list = filter_by_status(sites_list, status)

    # filtro por búsqueda
    q = request.GET.get('q')
    if q:
        sites_list = sites_list.filter(name__icontains=q)

    # paginación
    paginator = Paginator(sites_list, SITES_PER_PAGE)
    page = request.GET.get('p', '1')

    try:
        page_int = int(page)
    except:
        page_int = 1

    if page_int > paginator.num_pages or page_int < 0:
        page_int = paginator.num_pages

    # añadimos un factor para mostrar la numeración adecuada
    factor_adicional = (page_int - 1) * SITES_PER_PAGE

    try:
        sites = paginator.page(page)
    except PageNotAnInteger:
        sites = paginator.page(1)
    except EmptyPage:
        sites = paginator.page(paginator.num_pages)

    # últimos eventos
    sites_id = sites.object_list.values_list('id', flat=True)
    ultimos_eventos = ultimos_eventos_dict(sites_id)

    return render(request, 'websites.html', locals())


@login_required
def website(request, slug):
    """ Detalle de un Sitio """

    ultimo_dia = now() - timedelta(days=1)

    if slug:
        try:
            site = Site.objects.get(slug=slug)
            pings = site.pings.filter(date_time__gt=ultimo_dia).order_by('-date_time')[:75]
            ultimos_eventos = site.eventos.all().order_by('-date_time'
                                                          ).values_list('up', 'date_time')[:5]
        except Site.DoesNotExist:
            messages.error(request,
                           'No existe un registro para el sitio web seleccionado')
            return redirect('websites')

    return render(request, 'website.html', locals())


@login_required
def website_new(request):
    """ Registro de un nuevo sitio web """

    if request.method == 'POST':
        form = SiteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Se registró el sitio web satisfactoriamente')

            form = SiteForm()
    else:
        form = SiteForm()

    return render(request, 'website-registro.html', locals())


@login_required
def website_edit(request, slug):
    """ Edición de un nuevo sitio web """

    # initial
    if slug:
        try:
            site = Site.objects.get(slug=slug)
            initial = model_to_dict(site)

        except Site.DoesNotExist:
            messages.error(request,
                           'No existe un registro para el sitio web seleccionado')
            return redirect('website_new')
    else:
        return redirect('website_new')

    # form
    if request.method == 'POST':
        form = SiteEditForm(request.POST)

        if form.is_valid():
            form.update()
            messages.success(request, 'Se actualizó el registro')
    else:
        form = SiteEditForm(initial=initial)

    return render(request, 'website-edicion.html', locals())


@login_required
def website_alertas(request, slug):
    """ Ajuste de las alertas de caída de un sitio web (notificaciones) """

    # initial
    if slug:
        try:
            site = Site.objects.get(slug=slug)
        except Site.DoesNotExist:
            messages.error(request, 'No existe un registro para el sitio web seleccionado')
            return redirect('websites')
    else:
        return redirect('websites')

    # user
    usuario = request.user
    global_alertas_activas = (usuario.perfil.alertas_activas == 'off')

    usuarioWebsite, created = UsuarioWebsite.objects.get_or_create(site=site, usuario=usuario)
    initial = {'alerta_email': usuarioWebsite.alerta_email}

    # form
    if request.method == 'POST':
        form = UsuarioWebsiteForm(request.POST)

        if form.is_valid():
            form.save(usuario=usuario, site=site)
            messages.success(request, 'Se actualizó el registro')
    else:
        form = UsuarioWebsiteForm(initial=initial)

    return render(request, 'website-notificaciones.html', locals())


def website_delete(request, slug=None):
    """ Elimina un website """

    item = Site.objects.get(slug=slug)
    mensaje = u'Se eliminó el website {0}'.format(item.name)

    item.delete()
    messages.success(request, mensaje)

    return redirect('websites')


@login_required
def settings(request):
    """ Ajustes de usuario """

    user = request.user
    usuarioPerfil, created = UsuarioPerfil.objects.get_or_create(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        # formulario de edición de perfil
        if action == 'perfil':
            email = request.POST.get('email', '')
            if email:
                user.email = email
                user.save()
                messages.success(request, 'Se actualizó su cuenta de email.')
        # formulario de edición de alertas
        elif action == 'alertas':
            formAlerta = ConfigAlertasForm(request.POST)

            if formAlerta.is_valid():
                formAlerta.save(user)
                messages.success(request, 'Se actualizó la configuración.')
    else:
        formAlerta = ConfigAlertasForm(initial={
            'alertas': usuarioPerfil.alertas_activas
        })

    return render(request, 'ajustes.html', locals())


@login_required
def cancel_jobs(request):
    """ Cancela todos los trabajos """
    cancel_all_jobs()

    return HttpResponse('Trabajos cancelados')


def all_jobs(request):
    """ Muestra una lista de los trabajos en la consola """

    log.debug("::all_jobs::")

    for job in get_all_jobs():
        log.debug(job)

    return HttpResponse('Trabajos listados')
