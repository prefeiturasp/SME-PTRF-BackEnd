from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO
from ..models import FechamentoPeriodo, AcaoAssociacao, ContaAssociacao
from ..models.fechamento_periodo import STATUS_IMPLANTACAO


def implantacoes_de_saldo_da_associacao(associacao):
    saldos = []
    implantacoes = associacao.fechamentos_associacao.filter(status=STATUS_IMPLANTACAO).all()

    for implantacao in implantacoes:
        for aplicacao, total_aplicacao in [(APLICACAO_CAPITAL, 'total_receitas_capital'),
                                           (APLICACAO_CUSTEIO, 'total_receitas_custeio')]:
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

    if associacao.prestacoes_de_conta_da_associacao.exists():
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
            saldo=saldo['saldo']
        )

    return {
        'saldo_implantado': True,
        'codigo_erro': '',
        'mensagem': 'Saldos implantados com sucesso.',
    }
