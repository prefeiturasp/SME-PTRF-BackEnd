import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
    ContaAssociacao,
    Periodo,
    PeriodoPrevia,
)


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_demonstrativo_financeiro_async(periodo_uuid, conta_associacao_uuid, data_inicio, data_fim, usuario=""):
    logger.info('Iniciando task gerar_previa_demonstrativo_financeiro_async')

    logger.info(f'Iniciando criação da Previa de demonstrativo financeiro para a conta {conta_associacao_uuid} e período {periodo_uuid}.')

    from sme_ptrf_apps.core.services.prestacao_contas_services import (_criar_previa_demonstrativo_financeiro,
                                                                       _apagar_previas_demonstrativo_financeiro)

    periodo = Periodo.by_uuid(periodo_uuid)
    periodo_previa = PeriodoPrevia(periodo.uuid, periodo.referencia, data_inicio, data_fim)

    conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)

    acoes = conta_associacao.associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)

    _apagar_previas_demonstrativo_financeiro(conta=conta_associacao, periodo=periodo)

    demonstrativo_financeiro = _criar_previa_demonstrativo_financeiro(
        acoes=acoes,
        periodo=periodo,
        conta=conta_associacao,
        usuario=usuario,
    )

    logger.info(f'Previa de demonstrativo financeiro criado para a conta {conta_associacao} e período {periodo}.')
    logger.info(f'Previa de demonstrativo financeiro arquivo {demonstrativo_financeiro}.')
