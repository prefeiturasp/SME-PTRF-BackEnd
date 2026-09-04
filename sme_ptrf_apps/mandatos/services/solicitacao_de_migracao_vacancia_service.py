import logging
from typing import Optional
from django.db.models import QuerySet

from ..models import SolicitacaoDeMigracao

logger = logging.getLogger(__name__)


class ServicoSolicitacaoDeMigracaoVacancia:
    """ Dispara, de forma assíncrona, a migração de associações para o Histórico de Membros (v2). """

    def executa_migracoes(self, queryset: QuerySet) -> None:
        """ Dispara a task de migração de vacância para cada solicitação no queryset.

        Args:
            queryset (QuerySet): QuerySet contendo as solicitações de migração
        """

        logger.info(f"Iniciando serviço de migrações vacância para: {queryset}")
        for solicitacao in queryset.all():
            self.executa_migracao(solicitacao)

    def executa_migracao(self, solicitacao: SolicitacaoDeMigracao) -> None:
        """ Agenda a task assíncrona de migração vacância para uma única solicitação.

        Args:
            solicitacao: a `SolicitacaoDeMigracao` cuja migração vacância será agendada.
        """
        from ..tasks import solicitacao_de_migracao_vacancia_async

        logger.info(f"Iniciando a migração vacância do objeto: {solicitacao}")

        eol_unidade: Optional[str] = (
            solicitacao.eol_unidade.codigo_eol
            if solicitacao.eol_unidade and solicitacao.eol_unidade.codigo_eol else None
        )

        eol_dre: Optional[str] = (
            solicitacao.dre.codigo_eol
            if solicitacao.dre and solicitacao.dre.codigo_eol else None
        )

        solicitacao_de_migracao_vacancia_async.apply_async(
            (solicitacao.uuid, eol_unidade, eol_dre), countdown=1
        )
