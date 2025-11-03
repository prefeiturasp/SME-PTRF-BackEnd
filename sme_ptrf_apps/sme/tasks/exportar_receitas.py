import logging

from celery import shared_task
from sme_ptrf_apps.receitas.models.receita import Receita
from sme_ptrf_apps.sme.services.exporta_dados_creditos_service import ExportacoesDadosCreditosService

logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_receitas_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")
        
        queryset = Receita.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        ).order_by('id')
    else:
        queryset = Receita.objects.all()

    try:
        logger.info("Criando arquivo %s creditos_principal.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
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
