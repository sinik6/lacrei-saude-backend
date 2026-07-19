from django.db import models


class Appointment(models.Model):
    professional = models.ForeignKey(
        "professionals.Professional",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    data = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data"]
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        constraints = [
            models.UniqueConstraint(
                fields=["professional", "data"],
                name="uk_appointment_professional_data",
            ),
        ]

    def __str__(self):
        return f"Consulta com {self.professional.nome_social} em {self.data:%d/%m/%Y %H:%M}"
