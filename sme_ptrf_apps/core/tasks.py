import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
    Arquivo,
    Associacao,
    ContaAssociacao,
    Periodo,
    PeriodoPrevia,
    PrestacaoConta,
    Ata,
)


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def concluir_prestacao_de_contas_async(periodo_uuid, associacao_uuid, usuario="", criar_arquivos=True):
    from sme_ptrf_apps.core.services.prestacao_contas_services import (_criar_documentos, _criar_fechamentos,
                                                                       _apagar_previas_documentos)

    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)
    prestacao = PrestacaoConta.abrir(periodo=periodo, associacao=associacao)

    acoes = associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
    contas = associacao.contas.filter(status=ContaAssociacao.STATUS_ATIVA)

    _criar_fechamentos(acoes, contas, periodo, prestacao)
    logger.info('Fechamentos criados para a prestação de contas %s.', prestacao)

    _apagar_previas_documentos(contas=contas, periodo=periodo, prestacao=prestacao)
    logger.info('Prévias apagadas.')

    _criar_documentos(acoes, contas, periodo, prestacao, usuario=usuario, criar_arquivos=criar_arquivos)
    logger.info('Documentos gerados para a prestação de contas %s.', prestacao)

    prestacao = prestacao.concluir()
    logger.info('Concluída a prestação de contas %s.', prestacao)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},)
def processa_carga_async(arquivo_uuid):
    from sme_ptrf_apps.core.services import processa_carga
    logger.info("Processando arquivo %s", arquivo_uuid)
    arquivo = Arquivo.objects.filter(uuid=arquivo_uuid).first()
    if not arquivo:
        logger.info("Arquivo não encontrado %s", arquivo_uuid)
    else:
        logger.info("Arquivo encontrado %s", arquivo_uuid)
    processa_carga(arquivo)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_demonstrativo_financeiro_async(periodo_uuid, conta_associacao_uuid, data_inicio, data_fim, usuario=""):
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


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_relacao_de_bens_async(periodo_uuid, conta_associacao_uuid, data_inicio, data_fim):
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
    )

    logger.info(f'Previa de Relação de Bens criado para a conta {conta_associacao} e período {periodo}.')
    logger.info(f'Previa de Relação de Bens arquivo {relacao_de_bens}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_arquivo_ata_async(prestacao_de_contas_uuid, ata_uuid, usuario):
    logger.info(f'Iniciando criação do Arquivo da Ata, prestação {prestacao_de_contas_uuid} e ata {ata_uuid}')
    from sme_ptrf_apps.core.services.ata_service import gerar_arquivo_ata

    prestacao_de_contas = PrestacaoConta.by_uuid(prestacao_de_contas_uuid)
    ata = Ata.by_uuid(ata_uuid)

    arquivo_ata = gerar_arquivo_ata(prestacao_de_contas=prestacao_de_contas, ata=ata, usuario=usuario)

    if arquivo_ata is not None:
        logger.info(f'Arquivo ata: {arquivo_ata} gerado com sucesso.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_inicio_periodo_prestacao_de_contas_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_inicio_periodo_prestacao_de_contas

    logger.info(f'Iniciando a geração de notificação início período prestação de contas async')

    notificar_inicio_periodo_prestacao_de_contas()

    logger.info(f'Finalizando a geração de notificação início período prestação de contas async')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_pendencia_envio_prestacao_de_contas_async():
    logger.info(f'Iniciando a geração de notificação pendência envio prestação de contas async')

    from sme_ptrf_apps.core.services.notificacao_services import notificar_pendencia_envio_prestacao_de_contas

    notificar_pendencia_envio_prestacao_de_contas()

    logger.info(f'Finalizando a geração de notificação pendência envio prestação de contas async')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_proximidade_inicio_periodo_prestacao_conta_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_proximidade_inicio_periodo_prestacao_conta

    logger.info('Chamando serviço de notificação de proximidade do início do período de prestação de contas.')

    notificar_proximidade_inicio_periodo_prestacao_conta()

    logger.info('Executado serviço de notificação de proximidade do início do período de prestação de contas.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_proximidade_fim_periodo_prestacao_conta_async():
    from ..core.services.notificacao_services import notificar_proximidade_fim_periodo_prestacao_conta

    logger.info('Iniciando a geração de notificação de proximidade do fim do período de prestação de contas.')

    notificar_proximidade_fim_periodo_prestacao_conta()

    logger.info('Finalizando a geração de notificação de proximidade do fim do período de prestação de contas.')
