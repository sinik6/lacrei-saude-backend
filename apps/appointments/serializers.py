from rest_framework import serializers

from apps.appointments.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    professional_nome = serializers.CharField(source="professional.nome_social", read_only=True)

    class Meta:
        model = Appointment
        fields = ["id", "professional", "professional_nome", "data", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "professional_nome", "criado_em", "atualizado_em"]

    def validate_data(self, value):
        from django.utils.timezone import now

        if value < now():
            raise serializers.ValidationError("A data da consulta não pode estar no passado.")
        return value

    def validate(self, attrs):
        professional = attrs.get("professional")
        data = attrs.get("data")
        instance = self.instance

        if professional and data:
            qs = Appointment.objects.filter(professional=professional, data=data)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"data": "Já existe uma consulta para este profissional neste horário."}
                )
        return attrs
