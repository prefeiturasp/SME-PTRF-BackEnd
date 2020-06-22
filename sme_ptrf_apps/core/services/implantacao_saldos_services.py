from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO
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
                'conta_associacao':implantacao.conta_associacao,
                'aplicacao': aplicacao,
                'saldo': getattr(implantacao, total_aplicacao)
            }
            saldos.append(saldo)

    return saldos
