import logging

from celery import shared_task
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.sme.services.exporta_status_prestacoes_conta_service import ExportacoesStatusPrestacoesContaService


logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_status_prestacoes_contas_async(data_inicio, data_final, username, dre_uuid):
    logger.info("Exportando csv em processamento...")

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")
        
        queryset = PrestacaoConta.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        ).order_by('criado_em')
    else:
        queryset = PrestacaoConta.objects.all().order_by('criado_em')

    try:
        logger.info("Criando arquivo %s status_prestacoes_de_contas.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_uuid': dre_uuid,
            'dre_codigo_eol': dre_codigo_eol,
        }

        ExportacoesStatusPrestacoesContaService(
            **params,
            nome_arquivo='status_prestacoes_de_contas.csv'
        ).exporta_status_prestacoes_conta()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
