import logging

from celery import shared_task
from sme_ptrf_apps.core.models import ContaAssociacao
from sme_ptrf_apps.sme.services.exporta_dados_contas_service import ExportacaoDadosContasService

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_dados_conta_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")
    queryset = ContaAssociacao.objects.all()

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")
        
        queryset = queryset.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        )

    try:
        logger.info("Criando arquivo %s dados_contas.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
        }
        ExportacaoDadosContasService(
            **params,
            nome_arquivo='dados_contas.csv'
        ).exporta_contas_principal()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
