from ..models import PrestacaoConta, ContaAssociacao, Periodo, AcaoAssociacao, FechamentoPeriodo
from ..services import info_acoes_associacao_no_periodo
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
        especificacoes_despesas = RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo(
            acao_associacao=acao, periodo=periodo)
        FechamentoPeriodo.criar(
            prestacao_conta=prestacao,
            acao_associacao=acao,
            total_receitas_capital=totais_receitas['total_receitas_capital'],
            total_repasses_capital=totais_receitas['total_repasses_capital'],
            total_receitas_custeio=totais_receitas['total_receitas_custeio'],
            total_repasses_custeio=totais_receitas['total_repasses_custeio'],
            total_despesas_capital=totais_despesas['total_despesas_capital'],
            total_despesas_custeio=totais_despesas['total_despesas_custeio'],
            total_receitas_nao_conciliadas_capital=totais_receitas['total_receitas_nao_conciliadas_capital'],
            total_receitas_nao_conciliadas_custeio=totais_receitas['total_receitas_nao_conciliadas_custeio'],
            total_despesas_nao_conciliadas_capital=totais_despesas['total_despesas_nao_conciliadas_capital'],
            total_despesas_nao_conciliadas_custeio=totais_despesas['total_despesas_nao_conciliadas_custeio'],
            especificacoes_despesas=especificacoes_despesas
        )

    return prestacao


def salvar_prestacao_de_contas(prestacao_contas_uuid, observacoes):
    return PrestacaoConta.salvar(uuid=prestacao_contas_uuid, observacoes=observacoes)


def revisar_prestacao_de_contas(prestacao_contas_uuid, motivo):
    prestacao = PrestacaoConta.revisar(uuid=prestacao_contas_uuid, motivo=motivo)

    return prestacao


def informacoes_financeiras_para_atas(prestacao_contas):
    info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=prestacao_contas.associacao.uuid,
                                                  periodo=prestacao_contas.periodo,
                                                  conta=prestacao_contas.conta_associacao)
    info = {
        'uuid': prestacao_contas.uuid,
        'acoes': info_acoes,
        'totais': {},
    }
    return info
