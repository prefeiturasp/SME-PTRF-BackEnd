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
    time_limit=20000,
    soft_time_limit=20000
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

    SELECT_RELATED_RATEIOS = (
        'associacao__unidade__dre',
        'despesa__recurso',
        'despesa__tipo_documento',
        'despesa__tipo_transacao',
        'tipo_custeio',
        'especificacao_material_servico',
        'conta_associacao__tipo_conta',
        'acao_associacao__acao',
        'periodo_conciliacao',
        'tag',
    )

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")

        queryset = RateioDespesa.objects.select_related(*SELECT_RELATED_RATEIOS).filter(
            associacao__unidade__dre__uuid=dre_uuid,
        ).exclude(status=STATUS_INATIVO).order_by('id')
    else:
        queryset = RateioDespesa.objects.select_related(*SELECT_RELATED_RATEIOS).exclude(status=STATUS_INATIVO).order_by('id')  # noqa

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
