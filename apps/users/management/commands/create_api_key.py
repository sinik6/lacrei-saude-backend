from django.core.management.base import BaseCommand

from apps.users.models import ApiKey


class Command(BaseCommand):
    help = "Cria uma nova API Key para autenticação"

    def add_arguments(self, parser):
        parser.add_argument("--nome", type=str, required=True, help="Nome identificador da API Key")

    def handle(self, *args, **options):
        nome = options["nome"]
        api_key = ApiKey.objects.create(name=nome)
        self.stdout.write(self.style.SUCCESS("API Key criada com sucesso!"))
        self.stdout.write(f"  Nome: {api_key.name}")
        self.stdout.write(f"  Key:  {api_key.key}")
        self.stdout.write(self.style.WARNING("Guarde esta chave em local seguro."))
        self.stdout.write(self.style.WARNING("Use no header: X-API-Key: " + api_key.key))
