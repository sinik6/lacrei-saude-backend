from django.contrib import admin

from apps.appointments.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["professional", "data", "criado_em"]
    search_fields = ["professional__nome_social"]
    list_filter = ["data"]
    autocomplete_fields = ["professional"]
