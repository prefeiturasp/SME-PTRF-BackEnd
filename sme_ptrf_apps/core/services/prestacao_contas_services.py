from ..models import PrestacaoConta, ContaAssociacao, Periodo, AcaoAssociacao, FechamentoPeriodo
from ...despesas.models import RateioDespesa
from ...receitas.models import Receita


def iniciar_prestacao_de_contas(conta_associacao_uuid, periodo_uuid):
    conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
    periodo = Periodo.by_uuid(periodo_uuid)

    return PrestacaoConta.iniciar(conta_associacao=conta_associacao, periodo=periodo)

def concluir_prestacao_de_contas(prestacao_contas_uuid, observacoes):

    prestacao = PrestacaoConta.concluir(uuid=prestacao_contas_uuid, observacoes=observacoes)

    associacao = prestacao.associacao
    periodo = prestacao.periodo
    acoes = associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)

    for acao in acoes:
        totais_receitas = Receita.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo)
        totais_despesas = RateioDespesa.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo)
        FechamentoPeriodo.criar(
            prestacao_conta=prestacao,
            acao_associacao=acao,
            total_receitas_capital=totais_receitas['total_receitas_capital'],
            total_repasses_capital=totais_receitas['total_repasses_capital'],
            total_receitas_custeio=totais_receitas['total_receitas_custeio'],
            total_repasses_custeio=totais_receitas['total_repasses_custeio'],
            total_despesas_capital=totais_despesas['total_despesas_capital'],
            total_despesas_custeio=totais_despesas['total_despesas_custeio'],
        )

    return prestacao

def salvar_prestacao_de_contas(prestacao_contas_uuid):
    ...
