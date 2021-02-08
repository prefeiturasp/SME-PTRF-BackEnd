import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
    Arquivo,
    Associacao,
    ContaAssociacao,
    FechamentoPeriodo,
    Periodo,
    PrestacaoConta,
)

from sme_ptrf_apps.core.services.enviar_email import enviar_email_html

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},)
def concluir_prestacao_de_contas_async(periodo_uuid, associacao_uuid):
    from sme_ptrf_apps.core.services.prestacao_contas_services import _criar_documentos, _criar_fechamentos

    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)
    prestacao = PrestacaoConta.abrir(periodo=periodo, associacao=associacao)

    acoes = associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
    contas = associacao.contas.filter(status=ContaAssociacao.STATUS_ATIVA)

    _criar_fechamentos(acoes, contas, periodo, prestacao)
    logger.info('Fechamentos criados para a prestação de contas %s.', prestacao)

    _criar_documentos(acoes, contas, periodo, prestacao)
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

