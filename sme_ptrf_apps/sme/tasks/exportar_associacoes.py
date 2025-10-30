import logging

from celery import shared_task
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.sme.services.exporta_associacoes_service import ExportaAssociacoesService

logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_associacoes_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")
        
        queryset = Associacao.objects.filter(
            unidade__dre__uuid=dre_uuid,
        ).order_by('id')
    else:
        queryset = Associacao.objects.all().order_by('id')

    try:
        logger.info("Criando arquivo %s associacoes.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
        }

        ExportaAssociacoesService(
            **params,
            nome_arquivo='associacoes.csv'
        ).exporta_associacoes()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e