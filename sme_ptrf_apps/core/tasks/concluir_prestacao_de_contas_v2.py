import logging
import time

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
    Associacao,
    Periodo,
    PrestacaoConta,
    ObservacaoConciliacao,
    TaskCelery,
)
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def concluir_prestacao_de_contas_v2_async(
    id_task,
    periodo_uuid,
    associacao_uuid,
    username="",
    e_retorno_devolucao=False,
    requer_geracao_documentos=True,
    requer_geracao_fechamentos=False,
    requer_acertos_em_extrato=False,
    justificativa_acertos_pendentes='',
):
    from sme_ptrf_apps.core.services.prestacao_contas_services import (
        _criar_fechamentos,
        _apagar_previas_documentos,
    )

    task = TaskCelery.objects.get(uuid=id_task)

    logger.info('Iniciando a task concluir_prestacao_de_contas_async - VERSÃO 2')

    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)
    prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)

    pc_service = PrestacaoContaService(
        periodo_uuid=periodo_uuid,
        associacao_uuid=associacao_uuid,
        username=username,
    )

    task.grava_log_concatenado(f'Iniciando a task concluir_prestacao_de_contas_async - VERSÃO 2')

    time.sleep(10)  # Aguardar 10 segundos para iniciar a task e dar tempo de criar as tasks duplicadas

    tasks_ativas_dessa_pc = prestacao.tasks_celery_da_prestacao_conta.filter(
        nome_task='concluir_prestacao_de_contas_async').filter(finalizada=False).all()

    if tasks_ativas_dessa_pc.count() > 1:
        for task_ativa in tasks_ativas_dessa_pc:
            task_ativa.grava_log(
                f"Está PC possui mais de uma task de {task.nome_task} ativa no momento, "
                f"portanto o processo de concluir PC não será executado, será aguardado a criação de Falha de Geração."
            )

    elif tasks_ativas_dessa_pc.count() == 1:

        task.grava_log_concatenado(f'PC em processamento...')
        prestacao.em_processamento()

        acoes = associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
        contas = prestacao.contas_ativas_no_periodo()

        # Aqui grava observacao da conciliacao bancaria. Grava o campo observacao.justificativa_original com observacao.texto
        for conta_associacao in contas:
            observacao = ObservacaoConciliacao.objects.filter(
                periodo=periodo,
                conta_associacao=conta_associacao,
                associacao=associacao,
            ).first()
            if observacao:
                observacao.justificativa_original = observacao.texto
                observacao.save()

        # TODO Rever e simplificar as diversas condicionais abaixo
        if e_retorno_devolucao and (requer_geracao_documentos or requer_geracao_fechamentos):
            task.grava_log_concatenado(f'Solicitações de ajustes Justificadas requerem apagar fechamentos pc {prestacao.uuid}.')
            prestacao.apaga_fechamentos()

        if e_retorno_devolucao and requer_geracao_fechamentos and not requer_geracao_documentos:
            task.grava_log_concatenado(f'Solicitações de ajustes Justificadas requerem criar os fechamentos pc {prestacao.uuid}.')

            _criar_fechamentos(acoes, contas, periodo, prestacao)
            task.grava_log_concatenado(f'Fechamentos criados para a prestação de contas {prestacao}.')

        if e_retorno_devolucao and (requer_geracao_documentos or requer_acertos_em_extrato):
            task.grava_log_concatenado(f'Solicitações de ajustes requerem apagar fechamentos e documentos da pc {prestacao.uuid}.')

            # TODO: Verificar se os dados persistidos dos relatórios estão sendo apagados
            prestacao.apaga_relacao_bens()
            prestacao.apaga_demonstrativos_financeiros()
            task.grava_log_concatenado(f'Fechamentos e documentos da pc {prestacao.uuid} apagados.')

        if e_retorno_devolucao and not requer_geracao_fechamentos and not requer_geracao_documentos and not requer_acertos_em_extrato:
            task.grava_log_concatenado(f'Solicitações de ajustes NÃO requerem apagar fechamentos e documentos da pc {prestacao.uuid}.')

        if requer_geracao_documentos:
            _criar_fechamentos(acoes, contas, periodo, prestacao)
            task.grava_log_concatenado(f'Fechamentos criados para a prestação de contas {prestacao}.')

        if requer_geracao_documentos or requer_acertos_em_extrato:
            _apagar_previas_documentos(contas=contas, periodo=periodo, prestacao=prestacao)
            task.grava_log_concatenado(f'Prévias apagadas.')

            pc_service.persiste_dados_docs()
            task.grava_log_concatenado(f'Documentos gerados para a prestação de contas {prestacao}.')
        else:
            task.grava_log_concatenado(f'PC não requer geração de documentos e cálculo de fechamentos.')

        try:
            prestacao = prestacao.concluir_v2(
                e_retorno_devolucao=e_retorno_devolucao,
                justificativa_acertos_pendentes=justificativa_acertos_pendentes
            )

            task.grava_log_concatenado(f'Concluída a prestação de contas {prestacao}.')

            task = tasks_ativas_dessa_pc.first()
            task.registra_data_hora_finalizacao()
            task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração da relação de bens.')

        except Exception as e:
            task.grava_log_concatenado(f'Erro ao concluir a prestação de contas {prestacao}.')

            task = tasks_ativas_dessa_pc.first()
            task.registra_data_hora_finalizacao(log=e)
