from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (Site, Ping, Evento, UsuarioWebsite, UsuarioPerfil)


class SiteAdmin(admin.ModelAdmin):
    model = Site
    list_display = ('name', 'active', 'url')
    readonly_fields = ('slug',)
    search_fields = ('name',)


class PingAdmin(admin.ModelAdmin):
    model = Ping
    list_display = ('site', 'up', 'status_code', 'date_time', 'elapsed_time')
    readonly_fields = ('site', 'date_time', 'up', 'status_code', 'elapsed_time', 'mensaje')
    list_filter = ('up', 'site', 'date_time')


class EventoAdmin(admin.ModelAdmin):
    model = Evento
    list_display = ('site', 'up', 'date_time', 'last_event')
    list_filter = ('up', 'date_time')


class UsuarioWebsiteAdmin(admin.ModelAdmin):
    model = UsuarioWebsite
    list_display = ('site', 'usuario', 'alerta_email')


# Usuario
class UserProfileInline(admin.StackedInline):
    model = UsuarioPerfil
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


admin.site.register(Site, SiteAdmin)
admin.site.register(Ping, PingAdmin)
admin.site.register(Evento, EventoAdmin)
admin.site.register(UsuarioWebsite, UsuarioWebsiteAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
