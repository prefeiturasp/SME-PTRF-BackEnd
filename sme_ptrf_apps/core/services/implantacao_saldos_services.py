from decimal import Decimal
from django.db.models import Q
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import (APLICACAO_CAPITAL, APLICACAO_CUSTEIO,
                                                                     APLICACAO_LIVRE)
from ..models import FechamentoPeriodo, AcaoAssociacao, ContaAssociacao
from ..models.fechamento_periodo import STATUS_IMPLANTACAO


def implantacoes_de_saldo_da_associacao(associacao):
    saldos = []
    implantacoes = associacao.fechamentos_associacao.filter(status=STATUS_IMPLANTACAO).all()

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


def implanta_saldos_da_associacao(associacao, saldos):
    def saldos_duplicados(saldos):
        chaves_set = set()
        for saldo in saldos:
            chave = f'{saldo["acao_associacao"]}{saldo["conta_associacao"]}{saldo["aplicacao"]}'
            chaves_set.add(chave)
        return len(saldos) > len(chaves_set)

    if not associacao.periodo_inicial:
        return {
            'saldo_implantado': False,
            'codigo_erro': 'periodo_inicial_nao_definido',
            'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.',
        }

    periodo_primeira_pc = associacao.periodo_inicial.proximo_periodo if associacao.periodo_inicial else None

    if associacao.prestacoes_de_conta_da_associacao.exclude(
        Q(periodo=periodo_primeira_pc) & Q(status='DEVOLVIDA')
    ).exists():
        return {
            'saldo_implantado': False,
            'codigo_erro': 'prestacao_de_contas_existente',
            'mensagem': 'Os saldos não podem ser implantados, já existe uma prestação de contas da associação.',
        }

    if saldos_duplicados(saldos):
        return {
            'saldo_implantado': False,
            'codigo_erro': 'informacoes_repetidas',
            'mensagem': 'Existem valores repetidos de Ação, Conta e Aplicação. Verifique.',
        }

    associacao.apaga_implantacoes_de_saldo()

    for saldo in saldos:
        acao_associacao = AcaoAssociacao.by_uuid(saldo['acao_associacao'])
        conta_associacao = ContaAssociacao.by_uuid(saldo['conta_associacao'])
        FechamentoPeriodo.implanta_saldo(
            acao_associacao=acao_associacao,
            conta_associacao=conta_associacao,
            aplicacao=saldo['aplicacao'],
            saldo=Decimal(saldo['saldo'])
        )

    return {
        'saldo_implantado': True,
        'codigo_erro': '',
        'mensagem': 'Saldos implantados com sucesso.',
    }
