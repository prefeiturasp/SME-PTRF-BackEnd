import logging

from celery import shared_task
from sme_ptrf_apps.core.models.solicitacao_devolucao_ao_tesouro import SolicitacaoDevolucaoAoTesouro
from sme_ptrf_apps.sme.services.exporta_devolucao_tesouro_prestacoes_conta import (
    ExportacoesDevolucaoTesouroPrestacoesContaService
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=7400,
    soft_time_limit=7200
)
def exportar_devolucoes_ao_tesouro_async(data_inicio, data_final, username, dre_uuid):
    logger.info("Exportando csv em processamento...")

    _PC = (
        'solicitacao_acerto_lancamento__analise_lancamento__'
        'analise_prestacao_conta__prestacao_conta'
    )
    queryset = SolicitacaoDevolucaoAoTesouro.objects.select_related(
        f'{_PC}__associacao__unidade__dre',
        f'{_PC}__periodo__recurso',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa',
        'solicitacao_acerto_lancamento',
    ).prefetch_related(
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__rateios'
        '__tipo_custeio',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__rateios'
        '__especificacao_material_servico',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__rateios'
        '__conta_associacao__tipo_conta',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__rateios'
        '__acao_associacao__acao',
    )

    dre_codigo_eol = None
    if dre_uuid:
        from sme_ptrf_apps.core.models.unidade import Unidade
        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
            dre_codigo_eol = dre.codigo_eol
        except Unidade.DoesNotExist:
            logger.warning(f"DRE com uuid {dre_uuid} não encontrada")

        queryset = queryset.filter(
            solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__dre__uuid=dre_uuid,  # noqa
        )
    queryset = queryset.order_by(
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo_id',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta_id',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa_id',
        '-criado_em'
    ).distinct(
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo_id',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta_id',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa_id'
    )

    try:
        logger.info("Criando arquivo %s pcs_devolucoes_tesouro.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
            'dre_codigo_eol': dre_codigo_eol,
        }

        ExportacoesDevolucaoTesouroPrestacoesContaService(
            **params,
            nome_arquivo='pcs_devolucoes_tesouro.csv'
        ).exporta_devolucao_tesouro_pc()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
