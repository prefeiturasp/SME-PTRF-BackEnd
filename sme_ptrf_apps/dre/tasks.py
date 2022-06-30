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
    VerificacaoRegularidadeAssociacao, ConsolidadoDRE, Lauda
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
def verificar_se_gera_lauda(
    dre=None,
    periodo=None,
    consolidado_dre=None,
    usuario=None,
    tipo_contas=None,
    parcial=False
):
    if not parcial:
        ata = AtaParecerTecnico.objects.get(dre=dre, periodo=periodo, consolidado_dre=consolidado_dre)
        if ata and ata.preenchida_em:
            for tipo_conta in tipo_contas:
                gerar_lauda_txt_consolidado_dre_async(
                    consolidado_dre=consolidado_dre,
                    dre=dre,
                    periodo=periodo,
                    tipo_conta=tipo_conta,
                    parcial=parcial,
                    usuario=usuario
                )

        else:
            logger.info("Ata não preenchida, portanto não será gerada a Lauda")
    else:
        logger.info("Ainda constam prestações de contas das associações em análise, Lauda não será gerada")


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def verificar_se_gera_ata_parecer_tecnico_async(dre=None, periodo=None, consolidado_dre=None, usuario=None, ata=None):
    logger.info(f'Iniciando a verificação para gerar ata de parecer técnico')

    dre_uuid = dre.uuid
    periodo_uuid = periodo.uuid

    if ata and ata.preenchida_em:
        logger.info(f'Atrelando a Ata de Parecer Técnico {ata} ao Consolidado DRE {consolidado_dre}')
        ata.atrelar_consolidado_dre(consolidado_dre)
        logger.info(
            f'Iniciando a geração do Arquivo da Ata de Parecer Técnico da DRE {dre}, Período {periodo} e Consolidado DRE {consolidado_dre}')
        ata_uuid = ata.uuid
        gerar_arquivo_ata_parecer_tecnico_async(ata_uuid, dre_uuid, periodo_uuid, usuario)
    else:
        logger.info("Ata não preenchida, portanto Arquivo PDF não será gerado")


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

    for prestacao in prestacoes:
        logger.info(
            f'Passando Prestação de Contas para Publicada e Atrelando o Consolidado DRE: Prestação {prestacao}. Consolidado Dre {consolidado_dre}')
        prestacao.passar_para_publicada(consolidado_dre)


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
    ata_uuid=None
):
    tipo_contas = TipoConta.objects.all()

    dre = Unidade.dres.get(uuid=dre_uuid)
    periodo = Periodo.objects.get(uuid=periodo_uuid)
    ata = AtaParecerTecnico.objects.get(uuid=ata_uuid)

    for tipo_conta in tipo_contas:
        logger.info(f'Criando documento do Relatório Físico-Financeiro conta {tipo_conta}')

        tipo_conta_uuid = tipo_conta.uuid

        gerar_relatorio_consolidado_dre_async(
            dre_uuid=dre_uuid,
            periodo_uuid=periodo_uuid,
            tipo_conta_uuid=tipo_conta_uuid,
            usuario=usuario,
            parcial=parcial,
            consolidado_dre_uuid=consolidado_dre_uuid,
        )

    consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo)

    passar_pcs_do_relatorio_para_publicadas_async(
        dre=dre,
        periodo=periodo,
        consolidado_dre=consolidado_dre,
    )

    verificar_se_gera_ata_parecer_tecnico_async(
        dre=dre,
        periodo=periodo,
        consolidado_dre=consolidado_dre,
        usuario=usuario,
        ata=ata,
    )

    for tipo_conta in tipo_contas:

        gerar_lauda_txt_consolidado_dre_async(
            consolidado_dre=consolidado_dre,
            dre=dre,
            periodo=periodo,
            tipo_conta=tipo_conta,
            parcial=parcial,
            usuario=usuario
        )

    consolidado_dre.passar_para_status_gerado(parcial)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_arquivo_ata_parecer_tecnico_async(ata_uuid, dre_uuid, periodo_uuid, usuario):
    logger.info(f'Iniciando a geração da Ata de Parecer Técnico Async. DRE {dre_uuid} e Período {periodo_uuid}')
    from .services import gerar_arquivo_ata_parecer_tecnico

    ata = AtaParecerTecnico.by_uuid(ata_uuid)
    dre = Unidade.dres.get(uuid=dre_uuid)
    periodo = Periodo.by_uuid(periodo_uuid)

    arquivo_ata = gerar_arquivo_ata_parecer_tecnico(ata=ata, dre=dre, periodo=periodo, usuario=usuario)

    if arquivo_ata is not None:
        logger.info(f'Arquivo ata parecer técnico: {arquivo_ata} gerado com sucesso.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_relatorio_consolidado_dre_async(dre_uuid, periodo_uuid, parcial, tipo_conta_uuid, usuario,
                                          consolidado_dre_uuid):
    logger.info(f'Iniciando Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')

    # Remover excel
    # Essa linha esta sendo mantida para comparação do excel e pdf
    # Após aprovação do pdf, remover excel
    # from sme_ptrf_apps.dre.services import gera_relatorio_dre
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
        consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo)
    except ConsolidadoDRE.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        # Remover excel
        # Essa linha esta sendo mantida para comparação do excel e pdf
        # Após aprovação do pdf, remover excel
        # gera_relatorio_dre(dre, periodo, tipo_conta, parcial)
        _criar_demonstrativo_execucao_fisico_financeiro(dre, periodo, tipo_conta, usuario, parcial, consolidado_dre)

        # Comentei para remover posteriormente
        # AtaParecerTecnico.iniciar(
        #     dre=dre,
        #     periodo=periodo
        # )

    except Exception as err:
        erro = {
            'erro': 'problema_geracao_relatorio',
            'mensagem': 'Erro ao gerar relatório.'
        }
        logger.error("Erro ao gerar relatório consolidado: %s", str(err))
        raise Exception(erro)

    logger.info(f'Finalizado Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_previa_relatorio_consolidado_dre_async(dre_uuid, tipo_conta_uuid, periodo_uuid, parcial, usuario):
    logger.info(f'Iniciando Prévia Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')
    # Remover excel
    # Essa linha esta sendo mantida para comparação do excel e pdf
    # Após aprovação do pdf, remover excel
    # from sme_ptrf_apps.dre.services import gera_previa_relatorio_dre
    from sme_ptrf_apps.dre.services import _criar_previa_demonstrativo_execucao_fisico_financeiro

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
        # Remover excel
        # Essa linha esta sendo mantida para comparação do excel e pdf
        # Após aprovação do pdf, remover excel
        # gera_previa_relatorio_dre(dre, periodo, tipo_conta, parcial)
        _criar_previa_demonstrativo_execucao_fisico_financeiro(dre, periodo, tipo_conta, usuario, parcial)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_relatorio',
            'mensagem': 'Erro ao gerar relatório.'
        }
        logger.error("Erro ao gerar relatório consolidado: %s", str(err))
        raise Exception(erro)

    logger.info(f'Finalizado Prévia Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} Tipo Conta:{tipo_conta_uuid}.')


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
def gerar_lauda_txt_consolidado_dre_async(consolidado_dre, dre, tipo_conta, periodo, parcial, usuario):
    logger.info(
        f'Iniciando a geração do arquivo txt da lauda async. DRE:{dre} Período:{periodo} Tipo Conta:{tipo_conta} Consolidado DRE {consolidado_dre}.')
    from sme_ptrf_apps.dre.services import gerar_arquivo_lauda_txt_consolidado_dre

    usuario = get_user_model().objects.get(username=usuario)

    lauda = Lauda.criar_ou_retornar_lauda(
        consolidado_dre=consolidado_dre,
        dre=dre,
        periodo=periodo,
        tipo_conta=tipo_conta,
        usuario=usuario,
    )

    lauda.passar_para_status_em_processamento()

    logger.info(f"Objeto {lauda} criado/retornado com sucesso")

    try:
        ata = AtaParecerTecnico.objects.get(consolidado_dre=consolidado_dre, dre=dre, periodo=periodo)
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
        nome_conta = tipo_conta.nome.lower()
        gerar_arquivo_lauda_txt_consolidado_dre(lauda, dre, periodo, tipo_conta, ata, nome_dre, nome_conta, parcial)
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_txt',
            'mensagem': 'Erro ao gerar txt.'
        }
        logger.error("Erro ao gerar lauda: %s", str(err))
        raise Exception(erro)

    logger.info(
        f'Finalizado geração arquivo txt da lauda async. DRE:{dre} Período:{periodo} Tipo Conta:{tipo_conta}.')


# TODO: Remover este método, pois foi criado um novo acima quando desenvolvido o Consolidado DRE
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
