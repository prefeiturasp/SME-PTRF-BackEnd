from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Carga da tabela de especificações de materiais e serviços'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Importando tabela de especificações de materiais e serviços...'))

        contador = 0

        self.stdout.write(self.style.SUCCESS(
            'Nenhuma especificação importada.' if contador == 0 else f'Importado {contador} especificações.'))
        self.stdout.write(self.style.SUCCESS('Carga concluída.'))
