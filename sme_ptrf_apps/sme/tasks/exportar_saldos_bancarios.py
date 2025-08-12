import logging

from celery import shared_task
from sme_ptrf_apps.core.models.observacao_conciliacao import ObservacaoConciliacao
from sme_ptrf_apps.sme.services.exporta_dados_saldos_bancarios_service import ExportacaoDadosSaldosBancariosService

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_saldos_bancarios_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")

    if dre_uuid:
        queryset = ObservacaoConciliacao.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        )
    else:
        queryset = ObservacaoConciliacao.objects.all()

    try:
        logger.info("Criando arquivo %s saldo_bancario_unidades.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username
        }
        ExportacaoDadosSaldosBancariosService(
            **params,
            nome_arquivo='saldo_bancario_unidades.csv'
        ).exportar()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
