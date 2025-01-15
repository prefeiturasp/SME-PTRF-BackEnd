import logging

from celery import shared_task
from sme_ptrf_apps.receitas.models.receita import Receita
from sme_ptrf_apps.core.models.unidade import Unidade
from sme_ptrf_apps.sme.services.exporta_dados_unidades_service import ExportacoesDadosUnidadesService

logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=600,
    soft_time_limit=30000
)
def exportar_unidades_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")

    if dre_uuid:
        queryset = Unidade.objects.filter(
            dre__uuid=dre_uuid,
        ).order_by('uuid')
    else:
        queryset = Unidade.objects.all()

    try:
        logger.info("Criando arquivo %s unidades.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }
        ExportacoesDadosUnidadesService(
            **params,
            nome_arquivo='unidades.csv'
        ).exporta_unidades()
        logger.info("Gerando arquivo %s unidades.csv")

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
