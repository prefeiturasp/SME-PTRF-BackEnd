import time

from celery import shared_task

from sme_ptrf_apps.core.models import TaskCelery
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService
from sme_ptrf_apps.logging.loggers import ContextualLogger


@shared_task(
    bind=True,
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def calcular_prestacao_de_contas_async(
    self,
    id_task,
    periodo_uuid,
    associacao_uuid,
    username="",
    justificativa_acertos_pendentes='',
):
    calcular_pc_logger = ContextualLogger.get_logger(
        __name__,
        operacao='Prestação de Contas',
        username=username,
        task_id=str(id_task),
    )

    task = None
    prestacao = None
    try:
        task = TaskCelery.objects.get(uuid=id_task)

        task.registra_task_assincrona(self.request.id)

        # Apenas para informar que os logs não mais ficarão registrados na task.
        task.grava_log_concatenado('Iniciando a task calcular_prestacao_de_contas_async - VERSÃO 2. Logs registrados apenas no Kibana.')

        pc_service = PrestacaoContaService(
            periodo_uuid=periodo_uuid,
            associacao_uuid=associacao_uuid,
            username=username,
            logger=calcular_pc_logger
        )

        calcular_pc_logger.info(f'Iniciando a task calcular_prestacao_de_contas_async - VERSÃO 2')
        calcular_pc_logger.info(f'Prestação de contas: {pc_service.prestacao}')
        calcular_pc_logger.info(f'É retorno de devolução: {pc_service.e_retorno_devolucao}')
        calcular_pc_logger.info(f'Tem solicitações de mudança: {pc_service.pc_e_devolucao_com_solicitacoes_mudanca}')
        calcular_pc_logger.info(f'Tem solicitações de mudança realizadas: {pc_service.pc_e_devolucao_com_solicitacoes_mudanca_realizadas}')
        calcular_pc_logger.info(f'Tem acertos em extrato: {pc_service.pc_e_devolucao_com_solicitacao_acerto_em_extrato}')

        prestacao = pc_service.prestacao

        time.sleep(10)  # Aguardar 10 segundos para iniciar a task e dar tempo de criar as tasks duplicadas

        tasks_ativas_dessa_pc = prestacao.tasks_celery_da_prestacao_conta.filter(
            nome_task='concluir_prestacao_de_contas_async').filter(finalizada=False).all()

        if tasks_ativas_dessa_pc.count() > 1:
            raise Exception(
                f"Está PC possui mais de uma task de {task.nome_task} ativa no momento, "
                f"portanto o processo de concluir PC não será executado, será aguardado a criação de Falha de Geração."
            )

        calcular_pc_logger.info(f'PC em processamento...')
        prestacao.em_processamento()

        pc_service.atualiza_justificativa_conciliacao_original()

        if pc_service.requer_apagar_fechamentos:
            calcular_pc_logger.info(f'Apagando fechamentos existentes para a PC. Eles serão recalculados.')
            prestacao.apaga_fechamentos()
            calcular_pc_logger.info(f'Fechamentos apagados para a prestação de contas {prestacao}.')

        if pc_service.requer_apagar_documentos:
            calcular_pc_logger.info(
                f'Solicitações de ajustes requerem regerar os documentos da PC. Eles serão apagados para nova geração posterior.')

            calcular_pc_logger.info(f'Apagando relações de bens da PC.')
            prestacao.apaga_relacao_bens()
            calcular_pc_logger.info(f'Relações de bens apagadas.')

            calcular_pc_logger.info(f'Apagando demonstrativos financeiros da PC.')
            prestacao.apaga_demonstrativos_financeiros()
            calcular_pc_logger.info(f'Demonstrativos financeiros apagados.')

            calcular_pc_logger.info(f'Documentos da PC apagados.')

        if pc_service.requer_criar_fechamentos:
            pc_service.criar_fechamentos()
        else:
            calcular_pc_logger.info(f'Solicitações de ajustes NÃO requerem recalcular os fechamentos.')

        if pc_service.requer_gerar_documentos:
            pc_service.apagar_previas_documentos()
            pc_service.persiste_dados_docs()
        else:
            calcular_pc_logger.info(f'Solicitações de ajustes NÃO requerem gerar novamente os documentos da PC.')

        prestacao = prestacao.concluir_v2(
            e_retorno_devolucao=pc_service.e_retorno_devolucao,
            justificativa_acertos_pendentes=justificativa_acertos_pendentes
        )

        calcular_pc_logger.info(f'Concluída a prestação de contas {prestacao}.')

        task.registra_data_hora_finalizacao(f'Finalizada com sucesso o cálculo da PC.')
        calcular_pc_logger.info(f'Finalizado com sucesso a task calcular_prestacao_de_contas_async - VERSÃO 2')

    except Exception as e:
        mensagem_erro = f'Erro ao concluir a prestação de contas {prestacao}.'
        calcular_pc_logger.error(mensagem_erro, exc_info=True, stack_info=True)
        if task:
            task.registra_data_hora_finalizacao(mensagem_erro)
        raise e
