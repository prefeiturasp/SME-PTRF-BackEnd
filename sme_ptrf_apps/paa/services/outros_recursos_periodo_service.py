
from django.db import transaction

from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa


class ImportacaoUnidadesOutroRecursoException(Exception):
    """Exceção lançada quando ocorre erro na importação de unidades."""


class OutroRecursoPeriodoPaaService:

    @classmethod
    def importar_unidades(cls, destino: OutroRecursoPeriodoPaa, origem_uuid: str):
        if not origem_uuid:
            raise ImportacaoUnidadesOutroRecursoException(
                "origem_uuid é obrigatório."
            )

        origem = cls._obter_origem(origem_uuid)

        cls._validar_origem_destino(destino, origem)

        with transaction.atomic():
            cls._executar_importacao(destino, origem)

    @classmethod
    def _obter_origem(cls, origem_uuid: str) -> OutroRecursoPeriodoPaa:
        try:
            return OutroRecursoPeriodoPaa.objects.prefetch_related(
                'unidades'
            ).get(uuid=origem_uuid)
        except OutroRecursoPeriodoPaa.DoesNotExist:
            raise ImportacaoUnidadesOutroRecursoException(
                "Recurso de origem não encontrado."
            )

    @classmethod
    def _validar_origem_destino(cls, destino, origem):
        if destino.uuid == origem.uuid:
            raise ImportacaoUnidadesOutroRecursoException(
                "O recurso de origem não pode ser o mesmo que o destino."
            )

    @classmethod
    def _executar_importacao(cls, destino, origem):
        unidades = origem.unidades.all()

        if not unidades.exists():
            return

        destino.unidades.add(*unidades)
