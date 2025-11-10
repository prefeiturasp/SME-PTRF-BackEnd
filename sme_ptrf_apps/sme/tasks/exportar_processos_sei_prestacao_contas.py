import logging

from celery import shared_task
from sme_ptrf_apps.core.models.proccessos_associacao import ProcessoAssociacao
from sme_ptrf_apps.sme.services.exporta_dados_processos_sei_prestacoao_contas_service import ExportacaoDadosProcessosSEIPrestacaoContasService

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_processos_sei_prestacao_contas_async(username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")
        
        queryset = ProcessoAssociacao.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        )
    else:
        queryset = ProcessoAssociacao.objects.all()

    try:
        logger.info("Criando arquivo %s processo_sei_prestacao_contas.csv")
        params = {
            'queryset': queryset,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
        }
        ExportacaoDadosProcessosSEIPrestacaoContasService(
            **params,
            nome_arquivo='processo_sei_prestacao_contas.csv'
        ).exportar()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
