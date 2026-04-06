import logging

from celery import shared_task

from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_INATIVO
from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.sme.services.exporta_rateios_service import ExportacoesRateiosService


logger = logging.getLogger(__name__)

OPERACAO_EXPORTACAO_RATEIOS = 'Extração de dados - Rateios'


@shared_task(
    bind=True,
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300000
)
def exportar_rateios_async(self, data_inicio, data_final, username, dre_uuid=None):
    export_logger = ContextualLogger.get_logger(
        __name__,
        operacao=OPERACAO_EXPORTACAO_RATEIOS,
        username=username,
        task_id=str(self.request.id),
    )

    export_logger.info(
        'Iniciando exportar_rateios_async (despesas_classificacao_item.csv).',
        extra={
            'observacao': (
                f'data_inicio={data_inicio}, data_final={data_final}, dre_uuid={dre_uuid}'
            ),
        },
    )

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")

        queryset = RateioDespesa.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        ).exclude(status=STATUS_INATIVO).order_by('id')
    else:
        queryset = RateioDespesa.objects.exclude(status=STATUS_INATIVO).order_by('id')

    try:
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
        }

        ExportacoesRateiosService(
            **params,
            nome_arquivo='despesas_classificacao_item.csv'
        ).exporta_rateios()

    except Exception:
        export_logger.error(
            'Falha em exportar_rateios_async (despesas_classificacao_item.csv).',
            exc_info=True,
            stack_info=True,
        )
        raise

    export_logger.info('exportar_rateios_async finalizada com sucesso.')
