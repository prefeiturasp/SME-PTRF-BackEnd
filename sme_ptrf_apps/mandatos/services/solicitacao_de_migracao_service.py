import logging
from ..tasks import solicitacao_de_migracao_async

logger = logging.getLogger(__name__)


class ServicoSolicitacaoDeMigracao:

    def executa_migracoes(self, queryset):
        logger.info(f"Iniciando servico de migrações para: {queryset}")
        for solicitacao in queryset.all():
            self.executa_migracao(solicitacao)

    def executa_migracao(self, solicitacao):
        logger.info(f"Iniciando a migração do objeto: {solicitacao}")

        solicitacao_de_migracao_async.apply_async(
            (
                solicitacao.uuid,
                solicitacao.eol_unidade.codigo_eol if solicitacao.eol_unidade and solicitacao.eol_unidade.codigo_eol else None,
                solicitacao.dre.codigo_eol if solicitacao.dre and solicitacao.dre.codigo_eol else None,
            ), countdown=1
        )


