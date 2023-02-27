import logging
from django.db.models import Q

from celery import shared_task

from sme_ptrf_apps.core.models import (
    Periodo,
    Unidade,
    TipoConta,
    Associacao, PrestacaoConta
)

from sme_ptrf_apps.dre.models import (
    AtaParecerTecnico,
    AnoAnaliseRegularidade,
    AnaliseRegularidadeAssociacao,
    ItemVerificacaoRegularidade,
    VerificacaoRegularidadeAssociacao, ConsolidadoDRE, Lauda, JustificativaRelatorioConsolidadoDRE
)

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def verificar_se_gera_ata_parecer_tecnico_async(dre=None, periodo=None, consolidado_dre=None, usuario=None, ata=None, parcial=None):
    logger.info(f'Iniciando a verificação para gerar a Ata de Parecer Técnico')

    dre_uuid = dre.uuid
    periodo_uuid = periodo.uuid

    if ata and ata.preenchida_em:
        logger.info(f'Atrelando a Ata de Parecer Técnico {ata} ao Consolidado DRE {consolidado_dre}')
        ata.atrelar_consolidado_dre(consolidado_dre)
        logger.info(
            f'Iniciando a geração do Arquivo da Ata de Parecer Técnico da DRE {dre}, Período {periodo} '
            f'e Consolidado DRE {consolidado_dre}')
        ata_uuid = ata.uuid
        gerar_arquivo_ata_parecer_tecnico_async(ata_uuid, dre_uuid, periodo_uuid, usuario, parcial)
    else:
        logger.info("Ata não preenchida, portanto Arquivo PDF não será gerado")


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def atrelar_pc_ao_consolidado_dre_async(dre, periodo, consolidado_dre):
    dre_uuid = dre.uuid
    periodo_uuid = periodo.uuid

    prestacoes = PrestacaoConta.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre_uuid)
    prestacoes = prestacoes.filter(Q(status='APROVADA') | Q(status='APROVADA_RESSALVA') | Q(status='REPROVADA'))
    prestacoes = prestacoes.filter(publicada=False, consolidado_dre__isnull=True)

    for prestacao in prestacoes:
        logger.info(f'Atrelando Prestação ao Consolidado DRE: Prestação {prestacao}. Consolidado Dre {consolidado_dre}')
        consolidado_dre.vincular_pc_ao_consolidado(prestacao)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def passar_pcs_do_relatorio_para_publicadas_async(dre, periodo, consolidado_dre):
    dre_uuid = dre.uuid
    periodo_uuid = periodo.uuid

    prestacoes = PrestacaoConta.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre_uuid)
    prestacoes = prestacoes.filter(Q(status='APROVADA') | Q(status='APROVADA_RESSALVA') | Q(status='REPROVADA'))

    if consolidado_dre.eh_retificacao:
        # Retificacoes precisam filrar as PCs pelo consolidado vinculado

        prestacoes = prestacoes.filter(publicada=False, consolidado_dre=consolidado_dre)
    else:
        prestacoes = prestacoes.filter(publicada=False)

    for prestacao in prestacoes:
        logger.info(f'Passando Prestação de Contas para Publicada: Prestação {prestacao}')
        prestacao.passar_para_publicada()


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_previa_consolidado_dre_async(
    dre_uuid=None,
    periodo_uuid=None,
    parcial=None,
    usuario=None,
    consolidado_dre_uuid=None,
    sequencia_de_publicacao=None,
    apenas_nao_publicadas=False,
):
    dre = Unidade.dres.get(uuid=dre_uuid)
    periodo = Periodo.objects.get(uuid=periodo_uuid)

    if consolidado_dre_uuid:
        consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
    else:
        consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo,
                                                     sequencia_de_publicacao=sequencia_de_publicacao)

    if not consolidado_dre.eh_retificacao:
        # Uma retificacao ja possui suas PCs vinculadas

        atrelar_pc_ao_consolidado_dre_async(
            dre=dre,
            periodo=periodo,
            consolidado_dre=consolidado_dre,
        )

    gerar_previa_relatorio_consolidado_dre_async(
        dre_uuid=dre_uuid,
        periodo_uuid=periodo_uuid,
        usuario=usuario,
        parcial=parcial,
        consolidado_dre_uuid=consolidado_dre_uuid,
        sequencia_de_publicacao=sequencia_de_publicacao,
        apenas_nao_publicadas=apenas_nao_publicadas,
    )

    eh_parcial = parcial['parcial']
    consolidado_dre.passar_para_status_gerado(eh_parcial)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def verifica_se_relatorio_consolidado_deve_ser_gerado_async(dre, periodo, usuario):
    qtde_unidades_na_dre = Unidade.objects.filter(
        dre_id=dre,
    ).exclude(associacoes__cnpj__exact='').count()

    qtde_pcs_publicadas_no_periodo_pela_dre = PrestacaoConta.objects.filter(
        periodo=periodo,
        status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
        associacao__unidade__dre=dre,
        publicada=True
    ).count()

    if(int(qtde_unidades_na_dre) == int(qtde_pcs_publicadas_no_periodo_pela_dre)):
        concluir_consolidado_de_publicacoes_parciais_async(dre.uuid, periodo.uuid, usuario)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def concluir_consolidado_dre_async(
    dre_uuid=None,
    periodo_uuid=None,
    parcial=None,
    usuario=None,
    consolidado_dre_uuid=None,
    ata_uuid=None,
    sequencia_de_publicacao=None,
    apenas_nao_publicadas=False,
):
    tipo_contas = TipoConta.objects.all()

    dre = Unidade.dres.get(uuid=dre_uuid)
    periodo = Periodo.objects.get(uuid=periodo_uuid)
    ata = AtaParecerTecnico.objects.get(uuid=ata_uuid)

    if consolidado_dre_uuid:
        consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
    else:
        consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo,
                                                 sequencia_de_publicacao=sequencia_de_publicacao)


    if not consolidado_dre.eh_retificacao:
        # Uma retificacao ja possui suas PCs vinculadas

        atrelar_pc_ao_consolidado_dre_async(
            dre=dre,
            periodo=periodo,
            consolidado_dre=consolidado_dre,
        )

    # Atrelando consolidado as justificativas
    for tipo_conta in tipo_contas:
        justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
            dre=dre,
            tipo_conta=tipo_conta,
            periodo=periodo,
            consolidado_dre__isnull=True,
        ).last()

        if justificativa:
            justificativa.consolidado_dre = consolidado_dre
            justificativa.save()

    gerar_relatorio_consolidado_dre_async(
        dre_uuid=dre_uuid,
        periodo_uuid=periodo_uuid,
        usuario=usuario,
        parcial=parcial,
        consolidado_dre_uuid=consolidado_dre_uuid,
        sequencia_de_publicacao=sequencia_de_publicacao,
        apenas_nao_publicadas=apenas_nao_publicadas,
    )

    verificar_se_gera_ata_parecer_tecnico_async(
        dre=dre,
        periodo=periodo,
        consolidado_dre=consolidado_dre,
        usuario=usuario,
        ata=ata,
        parcial=parcial,
    )

    gerar_lauda_txt_consolidado_dre_async(
        consolidado_dre=consolidado_dre,
        dre=dre,
        periodo=periodo,
        parcial=parcial,
        usuario=usuario,
        apenas_nao_publicadas=apenas_nao_publicadas,
    )

    passar_pcs_do_relatorio_para_publicadas_async(
        dre=dre,
        periodo=periodo,
        consolidado_dre=consolidado_dre
    )

    eh_parcial = parcial['parcial']
    consolidado_dre.passar_para_status_gerado(eh_parcial)

    if(eh_parcial):
        verifica_se_relatorio_consolidado_deve_ser_gerado_async(
            dre=dre,
            periodo=periodo,
            usuario=usuario
        )

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def concluir_consolidado_de_publicacoes_parciais_async(
    dre_uuid=None,
    periodo_uuid=None,
    usuario=None,
):
    parcial = {
        "parcial": False,
        "sequencia_de_publicacao_atual": None,
    }

    gerar_relatorio_consolidado_dre_async(
        dre_uuid=dre_uuid,
        periodo_uuid=periodo_uuid,
        usuario=usuario,
        parcial=parcial,
        consolidado_dre_uuid=None,
        sequencia_de_publicacao=None,
        apenas_nao_publicadas=False,
        eh_consolidado_de_publicacoes_parciais=True,
    )



@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_arquivo_ata_parecer_tecnico_async(ata_uuid, dre_uuid, periodo_uuid, usuario, parcial):
    logger.info(f'Iniciando a geração da Ata de Parecer Técnico Async. DRE {dre_uuid} e Período {periodo_uuid}')
    from .services import gerar_arquivo_ata_parecer_tecnico

    ata = AtaParecerTecnico.by_uuid(ata_uuid)
    dre = Unidade.dres.get(uuid=dre_uuid)
    periodo = Periodo.by_uuid(periodo_uuid)

    arquivo_ata = gerar_arquivo_ata_parecer_tecnico(ata=ata, dre=dre, periodo=periodo, usuario=usuario, parcial=parcial)

    if arquivo_ata is not None:
        logger.info(f'Arquivo ata parecer técnico: {arquivo_ata} gerado com sucesso.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_relatorio_consolidado_dre_async(
    dre_uuid,
    periodo_uuid,
    parcial,
    usuario,
    consolidado_dre_uuid,
    sequencia_de_publicacao,
    apenas_nao_publicadas,
    eh_consolidado_de_publicacoes_parciais=False,
):
    logger.info(f'Iniciando Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid}')

    from sme_ptrf_apps.dre.services import _criar_demonstrativo_execucao_fisico_financeiro

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    consolidado_dre = None
    if not eh_consolidado_de_publicacoes_parciais:
        try:
            if consolidado_dre_uuid:
                consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
            else:
                consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo, sequencia_de_publicacao=sequencia_de_publicacao)

        except ConsolidadoDRE.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
            }
            logger.error('Erro: %r', erro)
            raise Exception(erro)

    try:
        _criar_demonstrativo_execucao_fisico_financeiro(dre, periodo, usuario, parcial, consolidado_dre, apenas_nao_publicadas, eh_consolidado_de_publicacoes_parciais)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_relatorio',
            'mensagem': 'Erro ao gerar relatório.'
        }
        logger.error("Erro ao gerar relatório consolidado: %s", str(err))
        raise Exception(erro)

    logger.info(f'Finalizado Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid}')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_previa_relatorio_consolidado_dre_async(
    dre_uuid,
    periodo_uuid,
    parcial,
    usuario,
    consolidado_dre_uuid,
    sequencia_de_publicacao,
    apenas_nao_publicadas,
):
    from sme_ptrf_apps.dre.services import _criar_previa_demonstrativo_execucao_fisico_financeiro

    logger.info(
        f'Iniciando a Prévia do Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} ')

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        if consolidado_dre_uuid:
            consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
        else:
            consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo,
                                                         sequencia_de_publicacao=sequencia_de_publicacao)
    except ConsolidadoDRE.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        _criar_previa_demonstrativo_execucao_fisico_financeiro(
            dre,
            periodo,
            usuario,
            consolidado_dre,
            parcial,
            apenas_nao_publicadas
        )
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_previa_relatorio',
            'mensagem': 'Erro ao gerar prévia do relatório.'
        }
        logger.error("Erro ao gerar prévia relatório consolidado: %s", str(err))
        raise Exception(erro)

    logger.info(
        f'Finalizado Prévia do Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid}')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_lauda_csv_async(dre_uuid, tipo_conta_uuid, periodo_uuid, parcial, username):
    logger.info(
        f'Iniciando a geração do arquivo csv da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')
    from sme_ptrf_apps.dre.services import gerar_csv
    from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download, atualiza_arquivo_download, \
        atualiza_arquivo_download_erro

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
    except TipoConta.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        nome_dre = dre.nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()

        nome_dre = nome_dre.lower()
        nome_conta = tipo_conta.nome.lower()
        obj_arquivo_download = gerar_arquivo_download(username, f"Lauda_{nome_dre}_{nome_conta}.csv")
        gerar_csv(dre, periodo, tipo_conta, obj_arquivo_download, parcial)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_csv',
            'mensagem': 'Erro ao gerar csv.'
        }
        logger.error("Erro ao gerar lauda: %s", str(err))
        raise Exception(erro)

    logger.info(
        f'Finalizado geração arquivo csv da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_lauda_txt_consolidado_dre_async(consolidado_dre, dre, periodo, parcial, usuario, apenas_nao_publicadas):
    logger.info(
        f'Iniciando a geração do arquivo txt da lauda async. DRE:{dre} Período:{periodo} Consolidado DRE {consolidado_dre}.')
    from sme_ptrf_apps.dre.services import gerar_arquivo_lauda_txt_consolidado_dre

    usuario = get_user_model().objects.get(username=usuario)

    lauda = Lauda.criar_ou_retornar_lauda(
        consolidado_dre=consolidado_dre,
        dre=dre,
        periodo=periodo,
        usuario=usuario,
    )

    lauda.passar_para_status_em_processamento()

    logger.info(f"Objeto {lauda} criado/retornado com sucesso")

    try:
        ata = AtaParecerTecnico.objects.filter(consolidado_dre=consolidado_dre, dre=dre, periodo=periodo).last()
        if not ata:
            raise ValidationError(f"O objeto Ata para a DRE {dre} e Período {periodo} não foi encontrado na base.")
    except (AtaParecerTecnico.DoesNotExist, ValidationError):
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto ata parecer tecnico para a dre {dre.uuid} e periodo {periodo.uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        nome_dre = dre.nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()

        nome_dre = nome_dre.lower()
        gerar_arquivo_lauda_txt_consolidado_dre(lauda, dre, periodo, ata, nome_dre, parcial, apenas_nao_publicadas)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_txt',
            'mensagem': 'Erro ao gerar txt.'
        }
        logger.error("Erro ao gerar lauda: %s", str(err))
        raise Exception(erro)

    logger.info(
        f'Finalizado geração arquivo txt da lauda async. DRE:{dre} Período:{periodo}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_lauda_txt_async(dre_uuid, tipo_conta_uuid, periodo_uuid, parcial, username):
    logger.info(
        f'Iniciando a geração do arquivo txt da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')
    from sme_ptrf_apps.dre.services import gerar_txt
    from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download, atualiza_arquivo_download, \
        atualiza_arquivo_download_erro

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
    except TipoConta.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    ata = AtaParecerTecnico.objects.filter(dre=dre).filter(periodo=periodo).last()

    if not ata:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto ata parecer tecnico para a dre {dre_uuid} e periodo {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        nome_dre = dre.nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()

        nome_dre = nome_dre.lower()
        nome_conta = tipo_conta.nome.lower()
        obj_arquivo_download = gerar_arquivo_download(username, f"Lauda_{nome_dre}_{nome_conta}.docx.txt")
        gerar_txt(dre, periodo, tipo_conta, obj_arquivo_download, ata, parcial)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_txt',
            'mensagem': 'Erro ao gerar txt.'
        }
        logger.error("Erro ao gerar lauda: %s", str(err))
        raise Exception(erro)

    logger.info(
        f'Finalizado geração arquivo txt da lauda async. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')


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


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_prazo_para_acerto_consolidado_dre_apos_vencimento_async():
    logger.info(f'Iniciando a geração de notificação prazo acerto apos vencimento async')

    from sme_ptrf_apps.dre.services.notificacao_service.notificacao_prazo_para_acerto_consolidado_devolucao import NotificacaoConsolidadoPrazoAcertoVencimento
    NotificacaoConsolidadoPrazoAcertoVencimento().notificar_prazo_para_acerto_apos_vencimento()

    logger.info(f'Finalizando a geração de notificação prazo acerto apos vencimento async')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_prazo_para_acerto_antes_vencimento_async():
    logger.info(f'Iniciando a geração de notificação prazo acerto antes vencimento async')

    from sme_ptrf_apps.dre.services.notificacao_service.notificacao_prazo_para_acerto_consolidado_devolucao import NotificacaoConsolidadoPrazoAcertoVencimento

    NotificacaoConsolidadoPrazoAcertoVencimento().notificar_prazo_para_acerto_antes_vencimento()

    logger.info(f'Finalizando a geração de notificação prazo acerto antes vencimento async')
