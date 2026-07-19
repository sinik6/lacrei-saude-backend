from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.professionals.models import Professional
from apps.professionals.serializers import ProfessionalSerializer


class ProfessionalViewSet(viewsets.ModelViewSet):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["profissao"]
    search_fields = ["nome_social", "profissao", "endereco"]
    ordering_fields = ["nome_social", "profissao", "criado_em"]
