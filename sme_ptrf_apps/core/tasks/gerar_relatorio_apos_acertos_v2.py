from celery import shared_task, current_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models.tasks_celery import TaskCelery
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
def gerar_relatorio_apos_acertos_v2_async(self, id_task, associacao_uuid, periodo_uuid, username=""):
    """
    Task para gerar o relatório após acertos da prestação de contas.
    Versão 2: Para rodar com o novo processo de PC.
    """
    # TODO: Após a migração para o novo processo de PC, renomear removendo o v2 e apagar o método antigo.
    from sme_ptrf_apps.core.services.analise_prestacao_conta_service import criar_relatorio_apos_acertos_final

    logger_rel_pos_acerto = ContextualLogger.get_logger(
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
        task.grava_log_concatenado('Iniciando a task gerar_relatorio_apos_acertos_v2_async. Logs registrados apenas no Kibana.')

        pc_service = PrestacaoContaService(
            periodo_uuid=periodo_uuid,
            associacao_uuid=associacao_uuid,
            username=username,
            logger=logger_rel_pos_acerto
        )

        logger_rel_pos_acerto.info(f'Iniciando a geração relatório após acertos da associacao.')

        ultima_analise_pc = pc_service.prestacao.analises_da_prestacao.order_by('id').last()
        if not ultima_analise_pc:
            raise Exception('Não foi possível encontrar a última análise da prestação de conta.')

        logger_rel_pos_acerto.info(f'Análise da prestação de conta: {ultima_analise_pc}')

        logger_rel_pos_acerto.info(f'Criando o relatório após acertos.')
        criar_relatorio_apos_acertos_final(analise_prestacao_conta=ultima_analise_pc, usuario=pc_service.usuario.name)
        logger_rel_pos_acerto.info(f'Relatório após acertos criado com sucesso.')

        task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração do relatório após acertos.')
    except Exception as exc:
        logger_rel_pos_acerto.error(
            f'A tentativa {tentativa} de gerar a relação de bens falhou.',
            exc_info=True,
            stack_info=True
        )
        if tentativa >= MAX_RETRIES:
            mensagem_tentativas_excedidas = 'Tentativas de reprocessamento com falha excedidas para o relaório após acertos.'
            logger_rel_pos_acerto.error(mensagem_tentativas_excedidas, exc_info=True, stack_info=True)

            if task:
                task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)

            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            raise exc
