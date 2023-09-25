import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AnalisePrestacaoConta,
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_relatorio_acertos_async(analise_prestacao_uuid, usuario=""):
    from sme_ptrf_apps.core.services.analise_prestacao_conta_service import (_criar_previa_relatorio_acertos)

    analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)

    analise_prestacao.apaga_arquivo_pdf()

    _criar_previa_relatorio_acertos(
        analise_prestacao_conta=analise_prestacao,
        usuario=usuario
    )

    logger.info('Finalizando a geração prévia do relatório de acertos')
