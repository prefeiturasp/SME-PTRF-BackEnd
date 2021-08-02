import logging

from django.db import transaction
from django.db.models import Q

from .demonstrativo_financeiro_xlsx_service import (gerar_arquivo_demonstrativo_financeiro_xlsx,
                                                    apagar_previas_demonstrativo_financeiro)
from ..models import PrestacaoConta, FechamentoPeriodo, Associacao, DemonstrativoFinanceiro, ObservacaoConciliacao
from ..services import info_acoes_associacao_no_periodo
from ..services.relacao_bens import gerar_arquivo_relacao_de_bens, apagar_previas_relacao_de_bens
from ..services.processos_services import get_processo_sei_da_prestacao
from ...despesas.models import RateioDespesa
from ...receitas.models import Receita
from ..tasks import concluir_prestacao_de_contas_async, gerar_previa_demonstrativo_financeiro_async

from ..services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from .demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf

logger = logging.getLogger(__name__)


@transaction.atomic
def concluir_prestacao_de_contas(periodo, associacao, usuario=""):
    prestacao = PrestacaoConta.abrir(periodo=periodo, associacao=associacao)
    logger.info(f'Aberta a prestação de contas {prestacao}.')

    prestacao.em_processamento()
    logger.info(f'Prestação de contas em processamento {prestacao}.')
    concluir_prestacao_de_contas_async.delay(periodo.uuid, associacao.uuid, usuario=usuario)

    return prestacao


def gerar_doc_previa_demonstrativo_financeiro(acoes, conta, periodo):
    logger.info(f'Criando assincronamente prévia de demonstrativo financeiro do período {periodo} e conta {conta}...')
    gerar_previa_demonstrativo_financeiro_async.delay(acoes=acoes, periodo=periodo, conta_associacao=conta)


def _criar_fechamentos(acoes, contas, periodo, prestacao):
    logger.info(f'Criando fechamentos do período {periodo} e prestacao {prestacao}...')
    for conta in contas:
        logger.info(f'Criando fechamentos da conta {conta}.')
        for acao in acoes:
            logger.info(f'Criando fechamentos da ação {acao}.')
            totais_receitas = Receita.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo,
                                                                            conta=conta)
            totais_despesas = RateioDespesa.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo,
                                                                                  conta=conta)
            especificacoes_despesas = RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo(
                acao_associacao=acao, periodo=periodo)
            FechamentoPeriodo.criar(
                prestacao_conta=prestacao,
                acao_associacao=acao,
                conta_associacao=conta,
                total_receitas_capital=totais_receitas['total_receitas_capital'],
                total_receitas_devolucao_capital=totais_receitas['total_receitas_devolucao_capital'],
                total_repasses_capital=totais_receitas['total_repasses_capital'],
                total_receitas_custeio=totais_receitas['total_receitas_custeio'],
                total_receitas_devolucao_custeio=totais_receitas['total_receitas_devolucao_custeio'],
                total_receitas_devolucao_livre=totais_receitas['total_receitas_devolucao_livre'],
                total_repasses_custeio=totais_receitas['total_repasses_custeio'],
                total_despesas_capital=totais_despesas['total_despesas_capital'],
                total_despesas_custeio=totais_despesas['total_despesas_custeio'],
                total_receitas_livre=totais_receitas['total_receitas_livre'],
                total_repasses_livre=totais_receitas['total_repasses_livre'],
                total_receitas_nao_conciliadas_capital=totais_receitas['total_receitas_nao_conciliadas_capital'],
                total_receitas_nao_conciliadas_custeio=totais_receitas['total_receitas_nao_conciliadas_custeio'],
                total_receitas_nao_conciliadas_livre=totais_receitas['total_receitas_nao_conciliadas_livre'],
                total_despesas_nao_conciliadas_capital=totais_despesas['total_despesas_nao_conciliadas_capital'],
                total_despesas_nao_conciliadas_custeio=totais_despesas['total_despesas_nao_conciliadas_custeio'],
                especificacoes_despesas=especificacoes_despesas
            )


def _criar_documentos(acoes, contas, periodo, prestacao, usuario, criar_arquivos=True):
    logger.info(f'Criando documentos do período {periodo} e prestacao {prestacao}...')

    for conta in contas:
        logger.info(f'Gerando relação de bens da conta {conta}.')
        gerar_arquivo_relacao_de_bens(
            periodo=periodo,
            conta_associacao=conta,
            prestacao=prestacao,
            criar_arquivos=criar_arquivos
        )

        logger.info(f'Gerando demonstrativo financeiro da conta {conta}.')
        _gerar_arquivos_demonstrativo_financeiro(
            acoes=acoes,
            periodo=periodo,
            conta_associacao=conta,
            usuario=usuario,
            prestacao=prestacao,
            criar_arquivos=criar_arquivos
        )


def _criar_previa_demonstrativo_financeiro(acoes, conta, periodo, usuario):
    logger.info(f'Gerando prévias do demonstrativo financeiro da conta {conta}.')

    _gerar_arquivos_demonstrativo_financeiro(
        acoes=acoes,
        periodo=periodo,
        conta_associacao=conta,
        prestacao=None,
        usuario=usuario,
        previa=True,
    )


def _criar_previa_relacao_de_bens(conta, periodo):
    logger.info(f'Criando prévia de demonstrativo financeiro do período {periodo} e conta {conta}...')
    gerar_arquivo_relacao_de_bens(periodo=periodo, conta_associacao=conta, previa=True)


def _apagar_previas_documentos(contas, periodo, prestacao):
    logger.info(f'Apagando prévias de documentos do período {periodo} e prestacao {prestacao}...')
    for conta in contas:
        logger.info(f'Apagando prévias de relações de bens da conta {conta}.')
        apagar_previas_relacao_de_bens(periodo=periodo, conta_associacao=conta)

        logger.info(f'Apagando prévias demonstrativo financeiro da conta {conta}.')
        apagar_previas_demonstrativo_financeiro(periodo=periodo, conta_associacao=conta)


def _apagar_previas_relacao_bens(conta, periodo):
    logger.info(f'Apagando prévias de relações de bens do período {periodo} e conta {conta}...')
    apagar_previas_relacao_de_bens(periodo=periodo, conta_associacao=conta)
    logger.info(f'Apagadas as prévias de relações de bens do período {periodo} e conta {conta}...')


def _apagar_previas_demonstrativo_financeiro(conta, periodo):
    logger.info(f'Apagando prévias de demonstrativos financeiros do período {periodo} e conta {conta}...')
    apagar_previas_demonstrativo_financeiro(periodo=periodo, conta_associacao=conta)
    logger.info(f'Apagadas prévias de demonstrativos financeiros do período {periodo} e conta {conta}...')


def reabrir_prestacao_de_contas(prestacao_contas_uuid):
    logger.info(f'Reabrindo a prestação de contas de uuid {prestacao_contas_uuid}.')
    concluido = PrestacaoConta.reabrir(uuid=prestacao_contas_uuid)
    if concluido:
        logger.info(f'Prestação de contas de uuid {prestacao_contas_uuid} foi reaberta. Seus registros foram apagados.')
    return concluido


def devolver_prestacao_de_contas(prestacao_contas_uuid):
    logger.info(f'Devolvendo a prestação de contas de uuid {prestacao_contas_uuid}.')
    prestacao = PrestacaoConta.devolver(uuid=prestacao_contas_uuid)
    return prestacao


def informacoes_financeiras_para_atas(prestacao_contas):
    def totaliza_info_acoes(info_acoes):
        totalizador = {
            'saldo_reprogramado': 0,
            'saldo_reprogramado_capital': 0,
            'saldo_reprogramado_custeio': 0,
            'saldo_reprogramado_livre': 0,

            'receitas_no_periodo': 0,

            'receitas_devolucao_no_periodo': 0,
            'receitas_devolucao_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_livre': 0,

            'repasses_no_periodo': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_custeio': 0,
            'repasses_no_periodo_livre': 0,

            'outras_receitas_no_periodo': 0,
            'outras_receitas_no_periodo_capital': 0,
            'outras_receitas_no_periodo_custeio': 0,
            'outras_receitas_no_periodo_livre': 0,

            'despesas_no_periodo': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_custeio': 0,

            'despesas_nao_conciliadas': 0,
            'despesas_nao_conciliadas_capital': 0,
            'despesas_nao_conciliadas_custeio': 0,

            'receitas_nao_conciliadas': 0,
            'receitas_nao_conciliadas_capital': 0,
            'receitas_nao_conciliadas_custeio': 0,
            'receitas_nao_conciliadas_livre': 0,

            'saldo_atual_custeio': 0,
            'saldo_atual_capital': 0,
            'saldo_atual_livre': 0,
            'saldo_atual_total': 0,

            'repasses_nao_realizados_capital': 0,
            'repasses_nao_realizados_custeio': 0,
            'repasses_nao_realizados_livre': 0
        }
        for info_acao in info_acoes:
            for key in totalizador.keys():
                totalizador[key] += info_acao[key]

        return totalizador

    logger.info(
        f'Get info financeiras para ata. Associacao:{prestacao_contas.associacao.uuid} Período:{prestacao_contas.periodo}')

    info_contas = []
    for conta_associacao in prestacao_contas.associacao.contas.all():
        logger.info(
            f'Get info financeiras por conta para a ata. Associacao:{prestacao_contas.associacao.uuid} Conta:{conta_associacao}')
        info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=prestacao_contas.associacao.uuid,
                                                      periodo=prestacao_contas.periodo,
                                                      conta=conta_associacao)

        info_acoes = [info for info in info_acoes if
                      info['saldo_reprogramado'] or info['receitas_no_periodo'] or info['despesas_no_periodo']]

        info_contas.append(
            {
                'conta_associacao': {
                    'uuid': f'{conta_associacao.uuid}',
                    'nome': f'{conta_associacao.tipo_conta.nome}',
                    'banco_nome': f'{conta_associacao.banco_nome}',
                    'agencia': f'{conta_associacao.agencia}',
                    'numero_conta': f'{conta_associacao.numero_conta}',
                },
                'acoes': info_acoes,
                'totais': totaliza_info_acoes(info_acoes),
            }
        )

    info = {
        'uuid': prestacao_contas.uuid,
        'contas': info_contas,
    }

    return info


def lista_prestacoes_de_conta_nao_recebidas(
    dre,
    periodo,
    filtro_nome=None, filtro_tipo_unidade=None, filtro_status=None
):
    associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').order_by(
        'unidade__tipo_unidade', 'unidade__nome')

    if filtro_nome is not None:
        associacoes_da_dre = associacoes_da_dre.filter(Q(nome__unaccent__icontains=filtro_nome) | Q(
            unidade__nome__unaccent__icontains=filtro_nome))

    if filtro_tipo_unidade is not None:
        associacoes_da_dre = associacoes_da_dre.filter(unidade__tipo_unidade=filtro_tipo_unidade)

    prestacoes = []
    for associacao in associacoes_da_dre:
        prestacao_conta = PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).first()

        # Devem entrar apenas Prestações de contas não apresentadas ou não recebidas
        if prestacao_conta and prestacao_conta.status not in [PrestacaoConta.STATUS_NAO_APRESENTADA,
                                                              PrestacaoConta.STATUS_NAO_RECEBIDA]:
            continue

        # Aplica o filtro por status
        if filtro_status == PrestacaoConta.STATUS_NAO_RECEBIDA:
            if not prestacao_conta or prestacao_conta.status != PrestacaoConta.STATUS_NAO_RECEBIDA:
                continue
        elif filtro_status == PrestacaoConta.STATUS_NAO_APRESENTADA:
            if prestacao_conta and prestacao_conta.status != PrestacaoConta.STATUS_NAO_APRESENTADA:
                continue

        info_prestacao = {
            'periodo_uuid': f'{periodo.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': get_processo_sei_da_prestacao(prestacao_contas=prestacao_conta) if prestacao_conta else '',
            'status': prestacao_conta.status if prestacao_conta else PrestacaoConta.STATUS_NAO_APRESENTADA,
            'tecnico_responsavel': '',
            'unidade_eol': associacao.unidade.codigo_eol,
            'unidade_nome': associacao.unidade.nome,
            'unidade_tipo_unidade': associacao.unidade.tipo_unidade,
            'uuid': f'{prestacao_conta.uuid}' if prestacao_conta else '',
            'associacao_uuid': f'{associacao.uuid}',
            'devolucao_ao_tesouro': '0,00'
        }

        prestacoes.append(info_prestacao)

    return prestacoes


def lista_prestacoes_de_conta_todos_os_status(
    dre,
    periodo,
    filtro_nome=None,
    filtro_tipo_unidade=None
):
    associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').order_by(
        'unidade__tipo_unidade', 'unidade__nome')

    if filtro_nome is not None:
        associacoes_da_dre = associacoes_da_dre.filter(Q(nome__unaccent__icontains=filtro_nome) | Q(
            unidade__nome__unaccent__icontains=filtro_nome))

    if filtro_tipo_unidade is not None:
        associacoes_da_dre = associacoes_da_dre.filter(unidade__tipo_unidade=filtro_tipo_unidade)

    prestacoes = []
    for associacao in associacoes_da_dre:
        prestacao_conta = PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).first()

        info_prestacao = {
            'periodo_uuid': f'{periodo.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': get_processo_sei_da_prestacao(prestacao_contas=prestacao_conta) if prestacao_conta else '',
            'status': prestacao_conta.status if prestacao_conta else PrestacaoConta.STATUS_NAO_APRESENTADA,
            'tecnico_responsavel': '',
            'unidade_eol': associacao.unidade.codigo_eol,
            'unidade_nome': associacao.unidade.nome,
            'unidade_tipo_unidade': associacao.unidade.tipo_unidade,
            'uuid': f'{prestacao_conta.uuid}' if prestacao_conta else '',
            'associacao_uuid': f'{associacao.uuid}',
            'devolucao_ao_tesouro': '0,00'
        }

        prestacoes.append(info_prestacao)

    return prestacoes


def _gerar_arquivos_demonstrativo_financeiro(acoes, periodo, conta_associacao, prestacao=None, usuario="",
                                             previa=False, criar_arquivos=True):

    logger.info(f'Criando registro do demonstrativo financeiro da conta {conta_associacao}.')
    demonstrativo, _ = DemonstrativoFinanceiro.objects.update_or_create(
        conta_associacao=conta_associacao,
        prestacao_conta=prestacao,
        periodo_previa=None if prestacao else periodo,
        versao=DemonstrativoFinanceiro.VERSAO_PREVIA if previa else DemonstrativoFinanceiro.VERSAO_FINAL,
        status=DemonstrativoFinanceiro.STATUS_EM_PROCESSAMENTO,
    )

    logger.info(f'Gerando demonstrativo financeiro em XLSX da conta {conta_associacao}.')

    try:
        observacao_conciliacao = ObservacaoConciliacao.objects.get(periodo__uuid=periodo.uuid, conta_associacao__uuid=conta_associacao.uuid)
    except Exception:
        observacao_conciliacao = None

    if criar_arquivos:
        demonstrativo = gerar_arquivo_demonstrativo_financeiro_xlsx(acoes=acoes, periodo=periodo,
                                                                    conta_associacao=conta_associacao,
                                                                    prestacao=prestacao,
                                                                    previa=previa,
                                                                    demonstrativo_financeiro=demonstrativo,
                                                                    observacao_conciliacao=observacao_conciliacao,
                                                                    )

    logger.info(f'Gerando demonstrativo financeiro em PDF da conta {conta_associacao}.')
    dados_demonstrativo = gerar_dados_demonstrativo_financeiro(usuario, acoes, periodo, conta_associacao,
                                                               prestacao, observacao_conciliacao=observacao_conciliacao, previa=False)

    logger.info(f'XXXXXXXXXXX DADOS | {dados_demonstrativo}')

    if criar_arquivos:
        gerar_arquivo_demonstrativo_financeiro_pdf(dados_demonstrativo, demonstrativo)

    demonstrativo.arquivo_concluido()

    return demonstrativo
