import logging

from celery import shared_task
from sme_ptrf_apps.sme.services.exporta_rateios_service import ExportacoesRateiosService
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_INATIVO


logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300000
)
def exportar_rateios_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")

    if dre_uuid:
        queryset = RateioDespesa.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        ).exclude(status=STATUS_INATIVO).order_by('id')
    else:
        queryset = RateioDespesa.objects.exclude(status=STATUS_INATIVO).order_by('id')

    try:
        logger.info("Criando arquivo %s despesas_classificacao_item.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesRateiosService(
            **params,
            nome_arquivo='despesas_classificacao_item.csv'
        ).exporta_rateios()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
