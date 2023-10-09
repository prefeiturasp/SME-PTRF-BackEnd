import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
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
def gerar_previa_relacao_de_bens_async(periodo_uuid, conta_associacao_uuid, data_inicio, data_fim, usuario):
    logger.info('Iniciando task gerar_previa_relacao_de_bens_async')

    logger.info(f'Iniciando criação da Previa de relação de bens para a conta {conta_associacao_uuid} e período {periodo_uuid}.')

    from sme_ptrf_apps.core.services.prestacao_contas_services import (_criar_previa_relacao_de_bens,
                                                                       _apagar_previas_relacao_bens)

    periodo = Periodo.by_uuid(periodo_uuid)
    periodo_previa = PeriodoPrevia(periodo.uuid, periodo.referencia, data_inicio, data_fim)

    conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)

    _apagar_previas_relacao_bens(conta=conta_associacao, periodo=periodo)

    relacao_de_bens = _criar_previa_relacao_de_bens(
        periodo=periodo,
        conta=conta_associacao,
        usuario=usuario
    )

    logger.info(f'Previa de Relação de Bens criado para a conta {conta_associacao} e período {periodo}.')
    logger.info(f'Previa de Relação de Bens arquivo {relacao_de_bens}.')
