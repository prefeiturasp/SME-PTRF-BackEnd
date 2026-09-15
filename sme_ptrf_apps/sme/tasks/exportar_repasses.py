import logging

from celery import shared_task
from sme_ptrf_apps.receitas.models import Repasse
from sme_ptrf_apps.sme.services.exporta_repasses_service import ExportacaoDadosRepassesService

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=7400,
    soft_time_limit=7200
)
def exportar_repasses_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")
    SELECT_RELATED = (
        'associacao__unidade__dre',
        'periodo__recurso',
        'conta_associacao__tipo_conta',
        'acao_associacao__acao',
        'carga_origem',
    )

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")

        queryset = Repasse.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        )
    else:
        queryset = Repasse.objects.all()

    queryset = queryset.select_related(*SELECT_RELATED).order_by('id')

    try:
        logger.info("Criando arquivo %s repasses.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
        }
        ExportacaoDadosRepassesService(
            **params,
            nome_arquivo='repasses.csv'
        ).exporta_repasses()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
