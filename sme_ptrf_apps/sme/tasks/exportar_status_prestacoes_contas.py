import logging

from celery import shared_task
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.sme.services.exporta_status_prestacoes_conta_service import ExportacoesStatusPrestacoesContaService


logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_status_prestacoes_contas_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = PrestacaoConta.objects.all().order_by('criado_em')

    try:
        logger.info("Criando arquivo %s status_prestacoes_de_contas.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesStatusPrestacoesContaService(
            **params,
            nome_arquivo='status_prestacoes_de_contas.csv'
        ).exporta_status_prestacoes_conta()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")