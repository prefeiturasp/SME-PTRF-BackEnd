import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def concluir_consolidado_de_publicacoes_parciais_async(
    dre_uuid=None,
    periodo_uuid=None,
    usuario=None,
):
    from ..services.consolidado_dre_service import gerar_relatorio_consolidado_dre

    parcial = {
        "parcial": False,
        "sequencia_de_publicacao_atual": None,
    }

    gerar_relatorio_consolidado_dre(
        dre_uuid=dre_uuid,
        periodo_uuid=periodo_uuid,
        usuario=usuario,
        parcial=parcial,
        consolidado_dre_uuid=None,
        sequencia_de_publicacao=None,
        apenas_nao_publicadas=False,
        eh_consolidado_de_publicacoes_parciais=True,
    )
