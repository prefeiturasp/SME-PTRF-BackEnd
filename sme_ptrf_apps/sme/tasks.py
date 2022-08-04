import logging

from celery import shared_task
from sme_ptrf_apps.receitas.models.receita import Receita
from sme_ptrf_apps.sme.services.exporta_dados_creditos_service import ExportacoesDadosCreditosService


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def exportar_receitas_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")
    queryset = Receita.objects.all()
    try:
        logger.info("Criando arquivo %s creditos_principal.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }
        ExportacoesDadosCreditosService(
            **params,
            nome_arquivo='creditos_principal.csv'
        ).exporta_creditos_principal()
        logger.info("Criando arquivo %s creditos_motivo_estorno.csv")
        ExportacoesDadosCreditosService(
            **params,
            nome_arquivo='creditos_motivos_estorno.csv'
        ).exporta_creditos_motivos_estorno()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
