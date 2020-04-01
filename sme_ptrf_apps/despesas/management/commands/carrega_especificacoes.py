from django.core.management.base import BaseCommand

from ...services.carga_especificacoes_material_servico import carrega_especificacoes


class Command(BaseCommand):
    help = 'Carga da tabela de especificações de materiais e serviços'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Importando tabela de especificações de materiais e serviços...'))

        carrega_especificacoes()

        self.stdout.write(self.style.SUCCESS('Carga concluída.'))
