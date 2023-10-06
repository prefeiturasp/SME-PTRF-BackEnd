import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    Associacao
)

from sme_ptrf_apps.dre.models import (
    AnoAnaliseRegularidade,
    AnaliseRegularidadeAssociacao,
    ItemVerificacaoRegularidade,
    VerificacaoRegularidadeAssociacao
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=333333,
    soft_time_limit=333333
)
def atualiza_regularidade_em_massa_async():
    logger.info(f"Iniciando serviço de atualização em massa de regularidade")
    anos_regularidade = AnoAnaliseRegularidade.objects.filter(atualizacao_em_massa=True).exclude(
        status_atualizacao=AnoAnaliseRegularidade.STATUS_ATUALIZACAO_EM_PROCESSAMENTO).order_by('ano')

    # Setando os anos selecionados para aguardando inicio do processo
    for ano in anos_regularidade:
        logger.info(f"setando ano selecionado: {ano}, para status de aguardando inicio")
        ano.status_atualizacao = AnoAnaliseRegularidade.STATUS_AGUARDANDO_INICIO_ATUALIZACAO
        ano.save()

    for ano in anos_regularidade:
        logger.info(f"Iniciando processo do ano: {ano}")
        ano.status_atualizacao = AnoAnaliseRegularidade.STATUS_ATUALIZACAO_EM_PROCESSAMENTO
        ano.save()

        associacoes_ativas = Associacao.ativas.all()

        for associacao in associacoes_ativas:
            analise, created_analise = AnaliseRegularidadeAssociacao.objects.update_or_create(
                ano_analise=ano,
                associacao=associacao,
                defaults={
                    'status_regularidade': AnaliseRegularidadeAssociacao.STATUS_REGULARIDADE_REGULAR
                }
            )

            items_verificacao = ItemVerificacaoRegularidade.objects.all()

            for item in items_verificacao:
                logger.info(f"Item: {item}")
                verificacao, created = VerificacaoRegularidadeAssociacao.objects.update_or_create(
                    analise_regularidade=analise,
                    item_verificacao=item,
                    defaults={
                        'regular': True
                    }
                )

                logger.info(f"{verificacao}")

        ano.atualizacao_em_massa = False
        ano.status_atualizacao = AnoAnaliseRegularidade.STATUS_ATUALIZACAO_CONCLUIDA
        ano.save()
        logger.info(f"Finalizado serviço de atualização em massa de regularidade")
