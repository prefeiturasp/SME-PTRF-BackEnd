from celery import shared_task, current_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models.demonstrativo_financeiro import DemonstrativoFinanceiro
from sme_ptrf_apps.core.services.demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf
from sme_ptrf_apps.core.services.recuperacao_dados_persistindos_demo_financeiro_service import \
    RecuperaDadosDemoFinanceiro
from sme_ptrf_apps.core.models.tasks_celery import TaskCelery
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService
from sme_ptrf_apps.logging.loggers import ContextualLogger

MAX_RETRIES = 3


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': MAX_RETRIES},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    time_limit=600,
    soft_time_limit=300
)
def gerar_demonstrativo_financeiro_async(id_task, prestacao_conta_uuid, username=""):
    dem_financ_logger = ContextualLogger.get_logger(
        __name__,
        operacao='Prestação de Contas',
        username=username,
        task_id=str(id_task),
    )
    tentativa = current_task.request.retries + 1

    task = None
    try:
        task = TaskCelery.objects.get(uuid=id_task)

        # Apenas para informar que os logs não mais ficarão registrados na task.
        task.grava_log_concatenado(
            f'Iniciando task gerar_demonstrativo_financeiro_async, tentativa {tentativa} da pc {prestacao_conta_uuid}. Logs registrados apenas no Kibana.')

        pc_service = PrestacaoContaService.from_prestacao_conta_uuid(
            prestacao_conta_uuid,
            username,
            dem_financ_logger
        )

        dem_financ_logger.info(f'Iniciando task gerar_demonstrativo_financeiro_async, tentativa {tentativa}.')

        if not pc_service.requer_gerar_documentos:
            dem_financ_logger.info(f'PC não requer geração de documentos. Demonstrativo financeiro não gerado.')
            return

        prestacao = pc_service.prestacao
        contas = prestacao.contas_ativas_no_periodo()

        for conta_associacao in contas:
            dem_financ_logger.info(
                f'Iniciando criação do demonstrativo financeiro para a conta {conta_associacao}.',
                extra={'observacao': f'uuid da conta: {conta_associacao.uuid}'}
            )

            demonstrativo = DemonstrativoFinanceiro.objects.get(
                conta_associacao_id=conta_associacao.id,
                prestacao_conta_id=prestacao.id
            )

            dados_recuperados = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

            gerar_arquivo_demonstrativo_financeiro_pdf(dados_recuperados, demonstrativo)

            demonstrativo.arquivo_concluido()

            dem_financ_logger.info(
                f'Demonstrativo financeiro criado para a conta {conta_associacao}',
                extra={'observacao': f'uuid da conta: {conta_associacao.uuid}'}
            )

            dem_financ_logger.info(f'Demonstrativo financeiro arquivo {demonstrativo.uuid}.')

        dem_financ_logger.info('Task gerar_demonstrativo_financeiro_async finalizada.')

        task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração do demonstrativo financeiro.')
    except Exception as exc:
        if task:
            dem_financ_logger.error(
                f'A tentativa {tentativa} de gerar o demonstrativo financeiro falhou.',
                exc_info=True,
                stack_info=True
            )

        if tentativa > MAX_RETRIES:
            mensagem_tentativas_excedidas = f'Tentativas de reprocessamento com falha excedidas para o demonstrativo financeiro.'
            dem_financ_logger.error(
                mensagem_tentativas_excedidas,
                exc_info=True,
                stack_info=True
            )

            if task:
                task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)

            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            raise exc
