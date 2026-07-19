from django.contrib import admin

from apps.users.models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "is_active", "criado_em"]
    search_fields = ["name"]
    list_filter = ["is_active"]
    readonly_fields = ["key"]
