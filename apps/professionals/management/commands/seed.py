from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand

from apps.appointments.models import Appointment
from apps.professionals.models import Professional


class Command(BaseCommand):
    help = "Popula o banco de dados com dados de exemplo"

    def _criar_profissionais(self):
        profissionais = [
            {
                "nome_social": "Dr. Alex Ferreira",
                "profissao": "Psicólogo",
                "endereco": "Rua Augusta, 1500, Sala 42 - Consolação, São Paulo - SP",
                "contato": "(11) 91234-5678",
            },
            {
                "nome_social": "Dra. Camila Santos",
                "profissao": "Clínica Geral",
                "endereco": "Av. Paulista, 2000, Sala 305 - Bela Vista, São Paulo - SP",
                "contato": "(11) 92345-6789",
            },
            {
                "nome_social": "Dr. Rafael Oliveira",
                "profissao": "Endocrinologista",
                "endereco": "Rua Oscar Freire, 900 - Jardins, São Paulo - SP",
                "contato": "(11) 93456-7890",
            },
            {
                "nome_social": "Dra. Julia Costa",
                "profissao": "Ginecologista",
                "endereco": "Rua Teodoro Sampaio, 1020 - Pinheiros, São Paulo - SP",
                "contato": "(11) 94567-8901",
            },
            {
                "nome_social": "Dr. Lucas Martins",
                "profissao": "Psiquiatra",
                "endereco": "Alameda Santos, 500 - Jardim Paulista, São Paulo - SP",
                "contato": "(11) 95678-9012",
            },
        ]

        created = []
        for dados in profissionais:
            obj, created_flag = Professional.objects.get_or_create(
                nome_social=dados["nome_social"],
                defaults=dados,
            )
            created.append(obj)
        return created

    def _criar_consultas(self, profissionais):
        base = datetime(2026, 8, 1, tzinfo=timezone.utc)
        horarios = [8, 9, 10, 11, 14, 15, 16, 17]
        total = 0

        for prof in profissionais:
            for j, hora in enumerate(horarios):
                dia = base + timedelta(days=j % 10)
                data = dia.replace(hour=hora)
                _, created_flag = Appointment.objects.get_or_create(
                    professional=prof,
                    data=data,
                )
                if created_flag:
                    total += 1

        return total

    def handle(self, *args, **options):
        self.stdout.write("Populando banco de dados...")

        profissionais = self._criar_profissionais()
        self.stdout.write(self.style.SUCCESS(f"  {len(profissionais)} profissionais criados"))

        consultas = self._criar_consultas(profissionais)
        self.stdout.write(self.style.SUCCESS(f"  {consultas} consultas criadas"))

        self.stdout.write(self.style.SUCCESS("Seed concluído com sucesso!"))
