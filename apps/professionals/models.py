from django.db import models


class Professional(models.Model):
    nome_social = models.CharField(max_length=255)
    profissao = models.CharField(max_length=255)
    endereco = models.TextField()
    contato = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome_social"]
        verbose_name = "Profissional da Saúde"
        verbose_name_plural = "Profissionais da Saúde"

    def __str__(self):
        return f"{self.nome_social} - {self.profissao}"
