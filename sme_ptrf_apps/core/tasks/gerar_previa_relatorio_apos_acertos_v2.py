from celery import shared_task, current_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models.tasks_celery import TaskCelery
from sme_ptrf_apps.core.models.analise_prestacao_conta import AnalisePrestacaoConta
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
def gerar_previa_relatorio_apos_acertos_v2_async(
    self,
    id_task,
    associacao_uuid,
    periodo_uuid,
    username="",
    analise_pc_uuid=None
):
    """
    Task para gerar o relatório após acertos da prestação de contas.
    Versão 2: Para rodar com o novo processo de PC.
    """
    # TODO: Após a migração para o novo processo de PC, renomear removendo o v2 e apagar o método antigo.
    from sme_ptrf_apps.core.services.analise_prestacao_conta_service import criar_previa_relatorio_apos_acertos

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
        task.grava_log_concatenado(
            'Iniciando a task gerar_previa_relatorio_apos_acertos_v2_async. Logs registrados apenas no Kibana.')

        pc_service = PrestacaoContaService(
            periodo_uuid=periodo_uuid,
            associacao_uuid=associacao_uuid,
            username=username,
            logger=logger_rel_pos_acerto
        )

        logger_rel_pos_acerto.info(f'Iniciando a geração prévia relatório após acertos da associacao.')

        if analise_pc_uuid:
            """
                Em casos de regeração do PDF, a analise pc uuid sera passada como parametro
            """

            analise_prestacao_conta = AnalisePrestacaoConta.by_uuid(uuid=analise_pc_uuid)
        else:
            """
                Em casos de geração do PDF pelo fluxo normal, sera pego a ultima analise da PC
            """

            analise_prestacao_conta = pc_service.prestacao.analises_da_prestacao.order_by('id').last()

        if not analise_prestacao_conta:
            raise Exception('Não foi possível encontrar a análise da prestação de conta.')

        logger_rel_pos_acerto.info(f'Análise da prestação de conta: {analise_prestacao_conta}')

        logger_rel_pos_acerto.info(f'Criando a prévia do relatório após acertos.')
        criar_previa_relatorio_apos_acertos(
            analise_prestacao_conta=analise_prestacao_conta,
            usuario=pc_service.usuario.name
        )
        logger_rel_pos_acerto.info(f'Prévia do relatório após acertos criado com sucesso.')

        task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração da prévia do relatório após acertos.')
    except Exception as exc:
        logger_rel_pos_acerto.error(
            f'A tentativa {tentativa} de gerar a prévia do relatório após acerto falhou.',
            exc_info=True,
            stack_info=True
        )
        if tentativa >= MAX_RETRIES:
            mensagem_tentativas_excedidas = 'Tentativas de reprocessamento com falha excedidas para a prévia do relatório após acertos.'
            logger_rel_pos_acerto.error(mensagem_tentativas_excedidas, exc_info=True, stack_info=True)

            if task:
                task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)

            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            raise exc
