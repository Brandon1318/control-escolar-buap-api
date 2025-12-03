from django.contrib import admin
from django.utils.html import format_html
from control_escolar_desit_api.models import *


@admin.register(Administradores)
@admin.register(Alumnos)
@admin.register(Maestros)

class ProfilesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
