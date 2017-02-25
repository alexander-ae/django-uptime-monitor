# -*- coding: utf-8 -*-

import logging

from django import forms

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

log = logging.getLogger('uptime')


class LoginForm(forms.Form):
    """ Formulario de acceso al sistema """

    username = forms.CharField()
    username.widget.attrs.update({'autofocus': 'autofocus', 'tabindex': '1',
                                  'required': 'required', 'placeholder': 'usuario'})

    password = forms.CharField(min_length=5, max_length=36,
                               widget=forms.PasswordInput)
    password.widget.attrs.update({'required': 'required', 'tabindex': '2',
                                  'placeholder': 'contraseña'})

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            mensaje = 'El usuario no ha sido registrado'
            log.error(mensaje)
            raise forms.ValidationError(mensaje)

        return username

    def auth(self):
        cd = self.cleaned_data
        return authenticate(username=cd['username'], password=cd['password'])
