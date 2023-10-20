import logging

from celery import shared_task
from sme_ptrf_apps.core.models.solicitacao_devolucao_ao_tesouro import SolicitacaoDevolucaoAoTesouro
from sme_ptrf_apps.sme.services.exporta_devolucao_tesouro_prestacoes_conta import ExportacoesDevolucaoTesouroPrestacoesContaService


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_devolucoes_ao_tesouro_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = SolicitacaoDevolucaoAoTesouro.objects.order_by('solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo_id', 'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta_id', 'solicitacao_acerto_lancamento__analise_lancamento__despesa_id', '-criado_em').distinct('solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo_id', 'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta_id', 'solicitacao_acerto_lancamento__analise_lancamento__despesa_id')

    try:
        logger.info("Criando arquivo %s pcs_devolucoes_tesouro.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDevolucaoTesouroPrestacoesContaService(
            **params,
            nome_arquivo='pcs_devolucoes_tesouro.csv'
        ).exporta_devolucao_tesouro_pc()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")