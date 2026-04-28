from decimal import Decimal
from django.db.models import Q
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import (APLICACAO_CAPITAL, APLICACAO_CUSTEIO,
                                                                     APLICACAO_LIVRE)
from ..models import FechamentoPeriodo, AcaoAssociacao, ContaAssociacao, PrestacaoConta
from ..models.fechamento_periodo import STATUS_IMPLANTACAO


def implantacoes_de_saldo_da_associacao(associacao, recurso=None):
    saldos = []
    implantacoes = associacao.fechamentos_associacao.filter(status=STATUS_IMPLANTACAO)
    if recurso:
        implantacoes = implantacoes.filter(periodo__recurso=recurso)
    implantacoes = implantacoes.all()

    for implantacao in implantacoes:
        for aplicacao, total_aplicacao in [(APLICACAO_CAPITAL, 'total_receitas_capital'),
                                           (APLICACAO_CUSTEIO, 'total_receitas_custeio'),
                                           (APLICACAO_LIVRE, 'total_receitas_livre')]:
            if not getattr(implantacao, total_aplicacao): continue

            saldo = {
                'acao_associacao': implantacao.acao_associacao,
                'conta_associacao': implantacao.conta_associacao,
                'aplicacao': aplicacao,
                'saldo': getattr(implantacao, total_aplicacao)
            }
            saldos.append(saldo)

    return saldos


def implanta_saldos_da_associacao(associacao, saldos, recurso=None):
    def saldos_duplicados(saldos):
        chaves_set = set()
        for saldo in saldos:
            chave = f'{saldo["acao_associacao"]}{saldo["conta_associacao"]}{saldo["aplicacao"]}'
            chaves_set.add(chave)
        return len(saldos) > len(chaves_set)

    periodo_inicial_associacao = associacao.get_periodo_inicial_associacao(recurso=recurso)
    periodo_inicial = periodo_inicial_associacao.periodo_inicial if periodo_inicial_associacao else None
    if not periodo_inicial and recurso and recurso.legado and associacao.periodo_inicial:
        if associacao.periodo_inicial.recurso_id == recurso.id:
            periodo_inicial = associacao.periodo_inicial
    if not periodo_inicial and not recurso and associacao.periodo_inicial:
        periodo_inicial = associacao.periodo_inicial

    if not periodo_inicial:
        return {
            'saldo_implantado': False,
            'codigo_erro': 'periodo_inicial_nao_definido',
            'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.',
        }

    periodo_primeira_pc = periodo_inicial.proximo_periodo if periodo_inicial else None

    prestacoes_de_conta = associacao.prestacoes_de_conta_da_associacao
    if recurso:
        prestacoes_de_conta = PrestacaoConta.filter_by_recurso(queryset=prestacoes_de_conta, recurso=recurso)

    if prestacoes_de_conta.exists():
        if not prestacoes_de_conta.filter(
            Q(periodo=periodo_primeira_pc) & Q(status='DEVOLVIDA')
        ).exists():
            return {
                'saldo_implantado': False,
                'codigo_erro': 'prestacao_de_contas_nao-encontrada',
                'mensagem': 'Os saldos não podem ser implantados, não existe uma prestação de contas do periodo inicial'
                            ' e devolivida.'
            }

    if saldos_duplicados(saldos):
        return {
            'saldo_implantado': False,
            'codigo_erro': 'informacoes_repetidas',
            'mensagem': 'Existem valores repetidos de Ação, Conta e Aplicação. Verifique.',
        }

    associacao.apaga_implantacoes_de_saldo(recurso=recurso, periodo=periodo_inicial)

    for saldo in saldos:
        acao_associacao = AcaoAssociacao.by_uuid(saldo['acao_associacao'])
        conta_associacao = ContaAssociacao.by_uuid(saldo['conta_associacao'])

        if recurso and acao_associacao.acao.recurso_id != recurso.id:
            return {
                'saldo_implantado': False,
                'codigo_erro': 'acao_nao_pertence_recurso',
                'mensagem': 'Há ação que não pertence ao recurso selecionado.',
            }

        if recurso and conta_associacao.tipo_conta.recurso_id != recurso.id:
            return {
                'saldo_implantado': False,
                'codigo_erro': 'conta_nao_pertence_recurso',
                'mensagem': 'Há conta que não pertence ao recurso selecionado.',
            }

        FechamentoPeriodo.implanta_saldo(
            acao_associacao=acao_associacao,
            conta_associacao=conta_associacao,
            aplicacao=saldo['aplicacao'],
            saldo=Decimal(saldo['saldo']),
            periodo=periodo_inicial
        )

    return {
        'saldo_implantado': True,
        'codigo_erro': '',
        'mensagem': 'Saldos implantados com sucesso.',
        'periodo': periodo_inicial,
    }
