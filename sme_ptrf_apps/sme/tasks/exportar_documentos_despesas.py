import logging

from celery import shared_task
from sme_ptrf_apps.despesas.models.despesa import Despesa
from sme_ptrf_apps.sme.services.exporta_documentos_despesas import ExportacoesDocumentosDespesasService


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300000
)
def exportar_documentos_despesas_async(data_inicio, data_final, username, dre_uuid):
    logger.info("Exportando csv em processamento...")

    queryset = Despesa.objects

    if dre_uuid:
        queryset = queryset.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        )

    queryset = queryset.order_by('id').order_by("criado_em")

    try:
        logger.info("Criando arquivo %s despesas_documento.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDocumentosDespesasService(
            **params,
            nome_arquivo='despesas_documento.csv'
        ).exporta_despesas()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
