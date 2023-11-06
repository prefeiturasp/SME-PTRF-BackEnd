import logging

from django.contrib.auth import get_user_model

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
    Associacao,
    Periodo,
    PrestacaoConta,
    ObservacaoConciliacao
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def concluir_prestacao_de_contas_async(
    periodo_uuid,
    associacao_uuid,
    usuario="",
    criar_arquivos=True,
    e_retorno_devolucao=False,
    requer_geracao_documentos=True,
    requer_geracao_fechamentos=False,
    requer_acertos_em_extrato=False,
    justificativa_acertos_pendentes='',
):
    import time

    logger.info('Iniciando a task concluir_prestacao_de_contas_async')

    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)
    prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)

    time.sleep(10)  # Aguardar 10 segundos para iniciar a task e dar tempo de criar as tasks duplicadas

    tasks_ativas_dessa_pc = prestacao.tasks_celery_da_prestacao_conta.filter(
        nome_task='concluir_prestacao_de_contas_async').filter(finalizada=False).all()

    if tasks_ativas_dessa_pc.count() > 1:
        for task in tasks_ativas_dessa_pc:
            task.grava_log(
                f"Está PC possui mais de uma task de {task.nome_task} ativa no momento, "
                f"portanto o processo de concluir PC não será executado, será aguardado a criação de Falha de Geração."
            )

    elif tasks_ativas_dessa_pc.count() == 1:
        from sme_ptrf_apps.core.services.prestacao_contas_services import (_criar_documentos, _criar_fechamentos,
                                                                           _apagar_previas_documentos)

        from sme_ptrf_apps.core.services.analise_prestacao_conta_service import (criar_relatorio_apos_acertos_final)

        from sme_ptrf_apps.core.services.falha_geracao_pc_service import FalhaGeracaoPcService

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

        if e_retorno_devolucao and (requer_geracao_documentos or requer_geracao_fechamentos):
            logging.info(f'Solicitações de ajustes Justificadas requerem apagar fechamentos pc {prestacao.uuid}.')
            prestacao.apaga_fechamentos()

        if e_retorno_devolucao and requer_geracao_fechamentos and not requer_geracao_documentos:
            logging.info(f'Solicitações de ajustes Justificadas requerem criar os fechamentos pc {prestacao.uuid}.')
            _criar_fechamentos(acoes, contas, periodo, prestacao)
            logger.info('Fechamentos criados para a prestação de contas %s.', prestacao)

        if e_retorno_devolucao and (requer_geracao_documentos or requer_acertos_em_extrato):
            logging.info(f'Solicitações de ajustes requerem apagar fechamentos e documentos da pc {prestacao.uuid}.')
            prestacao.apaga_relacao_bens()
            prestacao.apaga_demonstrativos_financeiros()
            logging.info(f'Fechamentos e documentos da pc {prestacao.uuid} apagados.')

        if e_retorno_devolucao and not requer_geracao_fechamentos and not requer_geracao_documentos and not requer_acertos_em_extrato:
            logging.info(f'Solicitações de ajustes NÃO requerem apagar fechamentos e documentos da pc {prestacao.uuid}.')

        if requer_geracao_documentos:
            _criar_fechamentos(acoes, contas, periodo, prestacao)
            logger.info('Fechamentos criados para a prestação de contas %s.', prestacao)

        if requer_geracao_documentos or requer_acertos_em_extrato:
            _apagar_previas_documentos(contas=contas, periodo=periodo, prestacao=prestacao)
            logger.info('Prévias apagadas.')

            _criar_documentos(acoes, contas, periodo, prestacao, usuario=usuario, criar_arquivos=criar_arquivos)
            logger.info('Documentos gerados para a prestação de contas %s.', prestacao)
        else:
            logger.info('PC não requer geração de documentos e cálculo de fechamentos.')

        try:
            prestacao = prestacao.concluir(
                e_retorno_devolucao=e_retorno_devolucao,
                justificativa_acertos_pendentes=justificativa_acertos_pendentes
            )

            # Aqui marcar como resolvido registro de falha
            usuario_notificacao = get_user_model().objects.get(username=usuario)
            logger.info('Iniciando a marcação como resolvido do registro de falha')
            marcar_como_resolvido_registro_de_falha = FalhaGeracaoPcService(
                usuario=usuario_notificacao,
                periodo=periodo,
                associacao=associacao
            )
            marcar_como_resolvido_registro_de_falha.marcar_como_resolvido()

            logger.info('Concluída a prestação de contas %s.', prestacao)

            task = tasks_ativas_dessa_pc.first()
            task.registra_data_hora_finalizacao()
        except Exception as e:
            logger.info('Erro ao concluir a prestação de contas %s.', prestacao)

            task = tasks_ativas_dessa_pc.first()
            task.registra_data_hora_finalizacao(log=e)
