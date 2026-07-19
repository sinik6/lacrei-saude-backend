from django.contrib import admin

from apps.professionals.models import Professional


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ["nome_social", "profissao", "contato", "criado_em"]
    search_fields = ["nome_social", "profissao", "contato"]
    list_filter = ["profissao"]
