from django.db import transaction
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa
import logging

logger = logging.getLogger(__name__)


class ImportacaoUnidadesOutroRecursoException(Exception):
    """Exceção lançada quando ocorre erro na importação de unidades."""


class OutroRecursoPeriodoPaaImportacaoService:
    """Importa unidades vinculadas entre recursos de um período do PAA."""

    @classmethod
    def importar_unidades(cls, destino: OutroRecursoPeriodoPaa, origem_uuid: str) -> None:
        """Importa as unidades de um recurso de origem para o recurso de destino.
        Args:
            destino: Recurso de período que receberá as unidades.
            origem_uuid: UUID do recurso que fornece as unidades.

        Raises:
            ImportacaoUnidadesOutroRecursoException: Se o UUID não for
                informado, a origem não existir ou origem e destino forem iguais.
        """
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
        """Obtém o recurso de período de origem pelo UUID.

        Args:
            origem_uuid: UUID do recurso de origem.

        Returns:
            Recurso de período correspondente ao UUID.

        Raises:
            ImportacaoUnidadesOutroRecursoException: Se o recurso não for
                encontrado.
        """
        try:
            return OutroRecursoPeriodoPaa.objects.prefetch_related(
                'unidades'
            ).get(uuid=origem_uuid)
        except OutroRecursoPeriodoPaa.DoesNotExist:
            raise ImportacaoUnidadesOutroRecursoException(
                "Recurso de origem não encontrado."
            )

    @classmethod
    def _validar_origem_destino(cls, destino: OutroRecursoPeriodoPaa, origem: OutroRecursoPeriodoPaa) -> None:
        """Valida que origem e destino são recursos distintos.

        Args:
            destino: Recurso que receberá as unidades.
            origem: Recurso que fornece as unidades.

        Raises:
            ImportacaoUnidadesOutroRecursoException: Se origem e destino forem
                o mesmo recurso.
        """
        if destino.uuid == origem.uuid:
            raise ImportacaoUnidadesOutroRecursoException(
                "O recurso de origem não pode ser o mesmo que o destino."
            )

    @classmethod
    def _executar_importacao(cls, destino: OutroRecursoPeriodoPaa, origem: OutroRecursoPeriodoPaa) -> None:
        """Copia as unidades da origem para o destino.

        Args:
            destino: Recurso que receberá as unidades.
            origem: Recurso que fornece as unidades.
        """
        unidades = origem.unidades.all()

        if not unidades.exists():
            return

        destino.unidades.add(*unidades)
