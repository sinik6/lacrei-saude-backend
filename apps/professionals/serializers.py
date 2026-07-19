from django.utils.html import strip_tags
from rest_framework import serializers

from apps.professionals.models import Professional


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ["id", "nome_social", "profissao", "endereco", "contato", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def validate_nome_social(self, value):
        return strip_tags(value).strip()

    def validate_profissao(self, value):
        return strip_tags(value).strip()

    def validate_endereco(self, value):
        return strip_tags(value).strip()

    def validate_contato(self, value):
        return strip_tags(value).strip()
