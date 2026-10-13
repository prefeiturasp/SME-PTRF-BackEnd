import logging

from celery import shared_task

from sme_ptrf_apps.core.services.relacao_bens import previa_relacao_de_bens_bloqueada
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

    # Antes de criar a prévia: se a FINAL já existe, não cria.
    # Para casos de concorrência
    if previa_relacao_de_bens_bloqueada(conta_associacao, periodo):
        logger.info(
            'Previa de relação de bens não gerada para a conta %s e período %s. '
            'Já existe documento final e a PC não está devolvida para acertos.',
            conta_associacao,
            periodo,
        )
        _apagar_previas_relacao_bens(conta=conta_associacao, periodo=periodo)
        return

    _apagar_previas_relacao_bens(conta=conta_associacao, periodo=periodo)

    relacao_de_bens = _criar_previa_relacao_de_bens(
        periodo=periodo,
        conta=conta_associacao,
        usuario=usuario
    )

    # Depois de criar a prévia: se a FINAL apareceu durante a geração, apaga a prévia.
    # Para casos de concorrência
    if previa_relacao_de_bens_bloqueada(conta_associacao, periodo):
        logger.info(
            'Previa de relação de bens descartada para a conta %s e período %s. '
            'Documento final passou a existir durante a geração.',
            conta_associacao,
            periodo,
        )
        _apagar_previas_relacao_bens(conta=conta_associacao, periodo=periodo)
        return

    logger.info(f'Previa de Relação de Bens criado para a conta {conta_associacao} e período {periodo}.')
    logger.info(f'Previa de Relação de Bens arquivo {relacao_de_bens}.')
