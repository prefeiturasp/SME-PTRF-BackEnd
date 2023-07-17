import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
    Arquivo,
    Associacao,
    ContaAssociacao,
    Periodo,
    PeriodoPrevia,
    PrestacaoConta,
    Ata,
    AnalisePrestacaoConta, Notificacao, ObservacaoConciliacao
)

from django.contrib.auth import get_user_model


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
    justificativa_acertos_pendentes='',
):
    from sme_ptrf_apps.core.services.prestacao_contas_services import (_criar_documentos, _criar_fechamentos,
                                                                       _apagar_previas_documentos)

    from sme_ptrf_apps.core.services.analise_prestacao_conta_service import (criar_relatorio_apos_acertos_final)

    from sme_ptrf_apps.core.services.falha_geracao_pc_service import FalhaGeracaoPcService

    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)
    prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)

    acoes = associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
    contas = associacao.contas.filter(status=ContaAssociacao.STATUS_ATIVA)

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

    if e_retorno_devolucao:
        ultima_analise_pc = prestacao.analises_da_prestacao.order_by('id').last()
        criar_relatorio_apos_acertos_final(analise_prestacao_conta=ultima_analise_pc, usuario=usuario)

    if e_retorno_devolucao and requer_geracao_fechamentos and not requer_geracao_documentos:
        logging.info(f'Solicitações de ajustes Justificadas requerem apagar fechamentos pc {prestacao.uuid}.')
        prestacao.apaga_fechamentos()
        logging.info(f'Solicitações de ajustes Justificadas requerem criar os fechamentos pc {prestacao.uuid}.')
        _criar_fechamentos(acoes, contas, periodo, prestacao)
        logger.info('Fechamentos criados para a prestação de contas %s.', prestacao)

    if e_retorno_devolucao and requer_geracao_documentos:
        logging.info(f'Solicitações de ajustes requerem apagar fechamentos e documentos da pc {prestacao.uuid}.')
        prestacao.apaga_fechamentos()
        prestacao.apaga_relacao_bens()
        prestacao.apaga_demonstrativos_financeiros()
        logging.info(f'Fechamentos e documentos da pc {prestacao.uuid} apagados.')
    else:
        logging.info(f'Solicitações de ajustes NÃO requerem apagar fechamentos e documentos da pc {prestacao.uuid}.')

    if requer_geracao_documentos:
        _criar_fechamentos(acoes, contas, periodo, prestacao)
        logger.info('Fechamentos criados para a prestação de contas %s.', prestacao)

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
    except:
        logger.info('Erro ao concluir a prestação de contas %s.', prestacao)



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


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_demonstrativo_financeiro_async(periodo_uuid, conta_associacao_uuid, data_inicio, data_fim, usuario=""):
    logger.info(f'Iniciando criação da Previa de demonstrativo financeiro para a conta {conta_associacao_uuid} e período {periodo_uuid}.')

    from sme_ptrf_apps.core.services.prestacao_contas_services import (_criar_previa_demonstrativo_financeiro,
                                                                       _apagar_previas_demonstrativo_financeiro)

    periodo = Periodo.by_uuid(periodo_uuid)
    periodo_previa = PeriodoPrevia(periodo.uuid, periodo.referencia, data_inicio, data_fim)

    conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)

    acoes = conta_associacao.associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)

    _apagar_previas_demonstrativo_financeiro(conta=conta_associacao, periodo=periodo)

    demonstrativo_financeiro = _criar_previa_demonstrativo_financeiro(
        acoes=acoes,
        periodo=periodo,
        conta=conta_associacao,
        usuario=usuario,
    )

    logger.info(f'Previa de demonstrativo financeiro criado para a conta {conta_associacao} e período {periodo}.')
    logger.info(f'Previa de demonstrativo financeiro arquivo {demonstrativo_financeiro}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_relacao_de_bens_async(periodo_uuid, conta_associacao_uuid, data_inicio, data_fim, usuario):
    logger.info(f'Iniciando criação da Previa de relação de bens para a conta {conta_associacao_uuid} e período {periodo_uuid}.')

    from sme_ptrf_apps.core.services.prestacao_contas_services import (_criar_previa_relacao_de_bens,
                                                                       _apagar_previas_relacao_bens)

    periodo = Periodo.by_uuid(periodo_uuid)
    periodo_previa = PeriodoPrevia(periodo.uuid, periodo.referencia, data_inicio, data_fim)

    conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)

    _apagar_previas_relacao_bens(conta=conta_associacao, periodo=periodo)

    relacao_de_bens = _criar_previa_relacao_de_bens(
        periodo=periodo,
        conta=conta_associacao,
        usuario=usuario
    )

    logger.info(f'Previa de Relação de Bens criado para a conta {conta_associacao} e período {periodo}.')
    logger.info(f'Previa de Relação de Bens arquivo {relacao_de_bens}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_arquivo_ata_async(prestacao_de_contas_uuid, ata_uuid, usuario):
    logger.info(f'Iniciando criação do Arquivo da Ata, prestação {prestacao_de_contas_uuid} e ata {ata_uuid}')
    from sme_ptrf_apps.core.services.ata_service import gerar_arquivo_ata

    prestacao_de_contas = PrestacaoConta.by_uuid(prestacao_de_contas_uuid)
    ata = Ata.by_uuid(ata_uuid)

    arquivo_ata = gerar_arquivo_ata(prestacao_de_contas=prestacao_de_contas, ata=ata, usuario=usuario)

    if arquivo_ata is not None:
        logger.info(f'Arquivo ata: {arquivo_ata} gerado com sucesso.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_inicio_periodo_prestacao_de_contas_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_inicio_periodo_prestacao_de_contas

    logger.info(f'Iniciando a geração de notificação início período prestação de contas async')

    notificar_inicio_periodo_prestacao_de_contas()

    logger.info(f'Finalizando a geração de notificação início período prestação de contas async')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_pendencia_envio_prestacao_de_contas_async():
    logger.info(f'Iniciando a geração de notificação pendência envio prestação de contas async')

    from sme_ptrf_apps.core.services.notificacao_services import notificar_pendencia_envio_prestacao_de_contas

    notificar_pendencia_envio_prestacao_de_contas()

    logger.info(f'Finalizando a geração de notificação pendência envio prestação de contas async')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_proximidade_inicio_periodo_prestacao_conta_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_proximidade_inicio_periodo_prestacao_conta

    logger.info('Chamando serviço de notificação de proximidade do início do período de prestação de contas async.')

    notificar_proximidade_inicio_periodo_prestacao_conta()

    logger.info('Executado serviço de notificação de proximidade do início do período de prestação de contas async.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_proximidade_fim_periodo_prestacao_conta_async():
    from ..core.services.notificacao_services import notificar_proximidade_fim_periodo_prestacao_conta

    logger.info('Iniciando a geração de notificação de proximidade do fim do período de prestação de contas async.')

    notificar_proximidade_fim_periodo_prestacao_conta()

    logger.info('Finalizando a geração de notificação de proximidade do fim do período de prestação de contas async.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_atraso_entrega_ajustes_prestacao_de_contas_async():
    from ..core.services.notificacao_services import notificar_atraso_entrega_ajustes_prestacao_de_contas
    logger.info('Iniciando a geração de notificação de atraso na entrega de ajustes de prestações de contas async.')

    notificar_atraso_entrega_ajustes_prestacao_de_contas()

    logger.info('Finalizando a geração de notificação de atraso na entrega de ajustes de prestações de contas async.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_proximidade_fim_prazo_ajustes_prestacao_conta_async():
    from ..core.services.notificacao_services import notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas

    logger.info('Iniciando a geração de notificação de proximidade do fim do prazo para entrega de ajustes de prestação de contas async.')

    notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas()

    logger.info('Finalizando a geração de notificação de proximidade do fim do prazo para entrega de ajustes de prestação de contas async.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_xlsx_extrato_dres_async(periodo_uuid, conta_uuid, username):
    logger.info('Iniciando a exportação do arquivo xlsx de extratos dres async')
    from sme_ptrf_apps.sme.services.exporta_arquivos_service import gerar_arquivo_xlsx_extrato_dres
    from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download, atualiza_arquivo_download, atualiza_arquivo_download_erro

    obj_arquivo_download = gerar_arquivo_download(username, "saldos_bancarios_associacoes.xlsx")
    try:
        arquivo_xlsx = gerar_arquivo_xlsx_extrato_dres(periodo_uuid, conta_uuid, username)
        atualiza_arquivo_download(obj_arquivo_download, arquivo_xlsx)
    except Exception as e:
        atualiza_arquivo_download_erro(obj_arquivo_download, e)

    logger.info('Finalizando a exportação do arquivo xlsx de saldos bancarios em detalhes associações async')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_relatorio_acertos_async(analise_prestacao_uuid, usuario=""):
    from sme_ptrf_apps.core.services.analise_prestacao_conta_service import (_criar_previa_relatorio_acertos)

    analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)

    analise_prestacao.apaga_arquivo_pdf()

    _criar_previa_relatorio_acertos(
        analise_prestacao_conta=analise_prestacao,
        usuario=usuario
    )

    logger.info('Finalizando a geração prévia do relatório de acertos')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_previa_relatorio_apos_acertos_async(analise_prestacao_uuid, usuario=""):
    from sme_ptrf_apps.core.services.analise_prestacao_conta_service import (criar_previa_relatorio_apos_acertos)

    analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)

    analise_prestacao.apaga_arquivo_pdf_relatorio_apos_acertos()

    criar_previa_relatorio_apos_acertos(
        analise_prestacao_conta=analise_prestacao,
        usuario=usuario
    )

    logger.info('Finalizando a geração prévia do relatório após acertos')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def cria_e_vincula_solicitacao_devolucao_ao_tesouro_async():
    from ..core.models import SolicitacaoAcertoLancamento, TipoAcertoLancamento, DevolucaoAoTesouro, SolicitacaoDevolucaoAoTesouro

    solicitacoes = SolicitacaoAcertoLancamento.objects.filter(tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_DEVOLUCAO).filter(
        solicitacao_devolucao_ao_tesouro=None).all().order_by(
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__nome',
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo')


    for solicitacao in solicitacoes:
        logger.info(f"Solicitacao: {solicitacao.id}")
        logger.info(f"Nome: {solicitacao.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome}")
        logger.info(f"EOL: {solicitacao.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol}")
        logger.info(f"Periodo: {solicitacao.analise_lancamento.analise_prestacao_conta.prestacao_conta.periodo}")
        logger.info("-------------------------------------------------")

        if solicitacao.devolucao_ao_tesouro:
            logger.info(f"Solicitação já possui uma devolução ao tesouro: {solicitacao.devolucao_ao_tesouro}")
            logger.info(f"Devolução ao tesouro id: {solicitacao.devolucao_ao_tesouro.id}")
            logging.info(f"Portanto sera ignorada!")
            continue

        despesa = solicitacao.analise_lancamento.despesa
        devolucao_ao_tesouro = DevolucaoAoTesouro.objects.filter(despesa=despesa).first()

        if devolucao_ao_tesouro:
            logger.info(f"Devolução ao tesouro encontrada {devolucao_ao_tesouro} - id: {devolucao_ao_tesouro.id}")

            solicitacao_criada = SolicitacaoDevolucaoAoTesouro.objects.create(
                solicitacao_acerto_lancamento=solicitacao,
                tipo=devolucao_ao_tesouro.tipo,
                devolucao_total=devolucao_ao_tesouro.devolucao_total,
                valor=devolucao_ao_tesouro.valor,
                motivo=devolucao_ao_tesouro.motivo
            )

            if solicitacao_criada:
                logger.info(f"Solicitação de devolução ao tesouro criada com sucesso! {solicitacao_criada} - id: {solicitacao_criada.id}")

                # Preenchendo informacões da solicitação de acerto
                solicitacao.detalhamento = devolucao_ao_tesouro.motivo
                solicitacao.devolucao_ao_tesouro = devolucao_ao_tesouro
                solicitacao.save()

                if devolucao_ao_tesouro.data:
                    # Se a devolução ao tesouro possui uma data, significa que a devolução ja foi atualizada em outra analise

                    solicitacao.analise_lancamento.devolucao_tesouro_atualizada = True
                    solicitacao.analise_lancamento.save()


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_encerramento_conta_bancaria_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_encerramento_conta_bancaria

    logger.info('Iniciando a geração de notificação de encerramento conta bancaria async.')

    notificar_encerramento_conta_bancaria()

    logger.info('Executado serviço de notificação de encerramento conta bancaria async.')
