# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import logout_then_login
from django.shortcuts import render, redirect
from django.template import RequestContext as ctx

from .forms import LoginForm

log = logging.getLogger('uptime')


# AUTH
def login_view(request):
    """ View personalizada para el login """

    if request.user.is_authenticated():
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.auth()

            if user is not None:
                if user.is_active:
                    user.last_login = datetime.now()
                    user.save()
                    login(request, user)

                    location = request.GET.get('next', None)

                    if location:
                        return redirect(location)

                    return redirect('dashboard')
                else:
                    messages.add_message(request, messages.WARNING,
                        'El usuario no se encuentra activo')
            else:
                messages.add_message(request, messages.ERROR,
                        u'El email y contraseña son inválidos')
        else:
            log.warning('Error de formulario')
    else:
        form = LoginForm()

    return render(request, 'login.html', locals())


def logout(request):
    """ Finaliza la sesión de un usuario """

    return logout_then_login(request, reverse('login'))
