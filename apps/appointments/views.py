from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.appointments.models import Appointment
from apps.appointments.serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related("professional").all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["professional"]
    search_fields = ["professional__nome_social"]
    ordering_fields = ["data", "criado_em"]
