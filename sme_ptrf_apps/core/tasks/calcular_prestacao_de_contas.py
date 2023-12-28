import logging
import traceback
import time

from celery import shared_task

from sme_ptrf_apps.core.models import TaskCelery
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def calcular_prestacao_de_contas_async(
    id_task,
    periodo_uuid,
    associacao_uuid,
    username="",
    e_retorno_devolucao=False,
    devolucao_tem_solicitacoes_mudanca=False,
    devolucao_tem_solicitacoes_mudanca_realizadas=True,
    devolucao_tem_acertos_em_extrato=False,
    justificativa_acertos_pendentes='',
):
    from sme_ptrf_apps.core.services.prestacao_contas_services import (
        _criar_fechamentos,
        _apagar_previas_documentos,
    )

    task = None
    prestacao = None
    try:
        task = TaskCelery.objects.get(uuid=id_task)

        task.grava_log_concatenado(f'Iniciando a task calcular_prestacao_de_contas_async - VERSÃO 2')

        task.grava_log_concatenado(f'É retorno de devolução: {e_retorno_devolucao}')
        task.grava_log_concatenado(f'Tem solicitações de mudança: {devolucao_tem_solicitacoes_mudanca}')
        task.grava_log_concatenado(f'Tem solicitações de mudança realizadas: {devolucao_tem_solicitacoes_mudanca_realizadas}')
        task.grava_log_concatenado(f'Tem acertos em extrato: {devolucao_tem_acertos_em_extrato}')

        pc_service = PrestacaoContaService(
            periodo_uuid=periodo_uuid,
            associacao_uuid=associacao_uuid,
            username=username,
        )

        periodo = pc_service.periodo
        prestacao = pc_service.prestacao
        acoes = pc_service.acoes
        contas = pc_service.contas

        time.sleep(10)  # Aguardar 10 segundos para iniciar a task e dar tempo de criar as tasks duplicadas

        tasks_ativas_dessa_pc = prestacao.tasks_celery_da_prestacao_conta.filter(
            nome_task='concluir_prestacao_de_contas_async').filter(finalizada=False).all()
        if tasks_ativas_dessa_pc.count() > 1:
            raise Exception(
                f"Está PC possui mais de uma task de {task.nome_task} ativa no momento, "
                f"portanto o processo de concluir PC não será executado, será aguardado a criação de Falha de Geração."
            )

        task.grava_log_concatenado(f'PC em processamento...')
        prestacao.em_processamento()

        pc_service.atualiza_justificativa_conciliacao_original()

        if e_retorno_devolucao and devolucao_tem_solicitacoes_mudanca:
            """
            Na verdade, não deveria haver fechamentos para a PC nesse caso, já que eles são apagados no ato da
            devolução quanto as solicitações de ajuste demandam alteração de lançamentos.
            Serão apagados aqui por segurança.
            """
            task.grava_log_concatenado(f'Apagando fechamentos existentes para a pc {prestacao.uuid}. Eles serão recalculados.')
            prestacao.apaga_fechamentos()
            task.grava_log_concatenado(f'Fechamentos apagados para a prestação de contas {prestacao}.')

        if e_retorno_devolucao and (devolucao_tem_solicitacoes_mudanca_realizadas or devolucao_tem_acertos_em_extrato):
            """
            No caso de devoluções de PC os documentos são regerados apenas se:
                - Houver solicitações de ajustes REALIZADAS e que demandem alteração de lançamentos,
                - Houver solicitações de ajustes nas informações de extrato.
            Nesses casos, os originais precisam ser apagados para que os novos sejam gerados.
            """
            task.grava_log_concatenado(
                f'Solicitações de ajustes requerem regerar os documentos da pc {prestacao.uuid}. Eles serão apagados para nova geração posterior.')

            prestacao.apaga_relacao_bens()
            task.grava_log_concatenado(f'Relações de bens apagadas.')

            prestacao.apaga_demonstrativos_financeiros()
            task.grava_log_concatenado(f'Demonstrativos financeiros apagados.')

            task.grava_log_concatenado(f'Documentos da pc {prestacao.uuid} apagados.')

        if (not e_retorno_devolucao) or devolucao_tem_solicitacoes_mudanca:
            """
            Fechamentos devem ser criados nas seguintes situações:
                - Na primeira geração de uma PC (quando não é uma devolução)
                - Devoluções com solicitações de ajustes que demandem alteração de lançamentos, realizadas ou não
            """
            task.grava_log_concatenado(f'Criando os fechamentos para pc {prestacao.uuid}.')
            _criar_fechamentos(acoes, contas, periodo, prestacao)
            task.grava_log_concatenado(f'Fechamentos criados para a prestação de contas {prestacao}.')
        else:
            task.grava_log_concatenado(f'Solicitações de ajustes NÃO requerem recalcular os fechamentos.')

        if (not e_retorno_devolucao) or (devolucao_tem_solicitacoes_mudanca_realizadas or devolucao_tem_acertos_em_extrato):
            """
            Os dados para os documentos da PC precisam ser calculados e persistidos nas seguintes situações:
                - Na primeira geração de uma PC (quando não é uma devolução)
                - Houver solicitações de ajustes REALIZADAS e que demandem alteração de lançamentos,
                - Houver solicitações de ajustes nas informações de extrato.
            Além disso, qualquer prévia de documento deve ser apagada, nas mesmas situações.
            """
            task.grava_log_concatenado(f'Apagando prévias de documentos da pc {prestacao.uuid}.')
            _apagar_previas_documentos(contas=contas, periodo=periodo, prestacao=prestacao)
            task.grava_log_concatenado(f'Prévias apagadas.')

            task.grava_log_concatenado(f'Persistindo dados dos documentos da pc {prestacao.uuid}.')
            pc_service.persiste_dados_docs()
            task.grava_log_concatenado(f'Dados dos documentos da {prestacao} persistidos para posterior geração dos PDFs.')

        if e_retorno_devolucao and not devolucao_tem_acertos_em_extrato and not devolucao_tem_solicitacoes_mudanca_realizadas:
            """
            Se a devolução não tiver solicitações de ajustes REALIZADAS que demandem alteração de lançamentos e
            nem solicitações de ajustes nas informações de extrato, não é necessário gerar novos documentos.
            """
            task.grava_log_concatenado(f'Solicitações de ajustes NÃO requerem gerar novamente os documentos da pc {prestacao.uuid}.')

        prestacao = prestacao.concluir_v2(
            e_retorno_devolucao=e_retorno_devolucao,
            justificativa_acertos_pendentes=justificativa_acertos_pendentes
        )

        task.grava_log_concatenado(f'Concluída a prestação de contas {prestacao}.')

        task.registra_data_hora_finalizacao(f'Finalizada com sucesso o cálculo da PC.')
        logger.info(f'Finalizado com sucesso a task calcular_prestacao_de_contas_async - VERSÃO 2')

    except Exception as e:
        traceback_info = traceback.format_exc()
        mensagem_erro = f'Erro ao concluir a prestação de contas {prestacao}. Detalhes do erro: {e}\n{traceback_info}'
        logger.error(mensagem_erro)
        if task:
            task.registra_data_hora_finalizacao(mensagem_erro)
        raise e
