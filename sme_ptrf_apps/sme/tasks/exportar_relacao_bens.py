import logging

from celery import shared_task
from sme_ptrf_apps.sme.services.exporta_relacao_bens_pc import ExportacoesDadosRelacaoBensService
from sme_ptrf_apps.core.models import RelacaoBens
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_INATIVO


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_relacao_bens_async(data_inicio, data_final, username, dre_uuid):
    logger.info("Exportando csv em processamento...")

    queryset = RelacaoBens.objects

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")
        
        queryset = queryset.filter(
            conta_associacao__associacao__unidade__dre__uuid=dre_uuid,
        )

    queryset = queryset.order_by('id')

    try:
        logger.info("Criando arquivo %s pcs_relacoes_bens.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
        }

        ExportacoesDadosRelacaoBensService(
            **params,
            nome_arquivo='pcs_relacoes_bens.csv'
        ).exporta_relacao_bens()
    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
