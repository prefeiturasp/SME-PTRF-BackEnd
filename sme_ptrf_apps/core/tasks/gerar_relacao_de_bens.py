from celery import shared_task, current_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models import  RelacaoBens, TaskCelery
from sme_ptrf_apps.core.services.relacao_bens import _retornar_dados_relatorio_relacao_de_bens
from sme_ptrf_apps.core.services.relacao_bens_pdf_service import gerar_arquivo_relacao_de_bens_pdf
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService
from sme_ptrf_apps.logging.loggers import ContextualLogger


MAX_RETRIES = 3


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': MAX_RETRIES},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    time_limit=600,
    soft_time_limit=300
)
def gerar_relacao_bens_async(self, id_task, prestacao_conta_uuid, username=""):
    rel_bens_logger = ContextualLogger.get_logger(
        __name__,
        operacao='Prestação de Contas',
        username=username,
        task_id=str(id_task),
    )
    tentativa = current_task.request.retries + 1

    task = None
    try:
        task = TaskCelery.objects.get(uuid=id_task)

        task.registra_task_assincrona(self.request.id)

        # Apenas para informar que os logs não mais ficarão registrados na task.
        task.grava_log_concatenado(
            f'Iniciando task gerar_relacao_bens_async, tentativa {tentativa} da pc {prestacao_conta_uuid}. Logs registrados apenas no Kibana.')

        pc_service = PrestacaoContaService.from_prestacao_conta_uuid(
            prestacao_conta_uuid,
            username,
            rel_bens_logger
        )

        rel_bens_logger.info(f'Iniciando task gerar_relacao_bens_async, tentativa {tentativa}.')

        if not pc_service.requer_gerar_documentos:
            rel_bens_logger.info(f'PC não requer geração de documentos. Relação de bens não gerada.')
            return

        prestacao = pc_service.prestacao

        relacao_bens = prestacao.relacoes_de_bens_da_prestacao.filter(versao=RelacaoBens.VERSAO_FINAL)

        for relacao in relacao_bens:
            dados = _retornar_dados_relatorio_relacao_de_bens(relacao)

            if dados:
                gerar_arquivo_relacao_de_bens_pdf(dados, relacao)
                relacao.arquivo_concluido()
                rel_bens_logger.info(f'Arquivo relação bens PDF gerado para a conta {relacao.conta_associacao}.')
            else:
                rel_bens_logger.warning(
                    f'Dados persistidos da relação de bens não encontrados.',
                    extra={'observacao': f'relacao: {relacao}'}
                )

        rel_bens_logger.info('Task gerar_arquivo_final_relacao_bens_async finalizada')
        task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração da relação de bens.')
    except Exception as exc:
        rel_bens_logger.error(f'A tentativa {tentativa} de gerar a relação de bens falhou.', exc_info=True, stack_info=True)

        if tentativa > MAX_RETRIES:
            mensagem_tentativas_excedidas = f'Tentativas de reprocessamento com falha excedidas para a relação de bens.'
            rel_bens_logger.error(mensagem_tentativas_excedidas, exc_info=True, stack_info=True)

            if task:
                task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)

            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            raise exc
