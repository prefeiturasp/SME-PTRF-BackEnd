import pytest
from model_bakery import baker

from ...models import PrestacaoConta


pytestmark = pytest.mark.django_db


@pytest.fixture
def tpcccm_prestacao_conta(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def tpcccm_receita(associacao, conta_associacao_cheque, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas,
        valor=1000.00,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


def test_contas_com_movimento_de_entrada(
    tpcccm_prestacao_conta: PrestacaoConta,
    tpcccm_receita,
    conta_associacao_cheque,
    conta_associacao_cartao
):
    contas_com_movimento = tpcccm_prestacao_conta.get_contas_com_movimento()

    assert len(contas_com_movimento) == 1
    assert contas_com_movimento[0] == conta_associacao_cheque


@pytest.fixture
def tpcccm_despesa(associacao, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=periodo.data_inicio_realizacao_despesas,
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas,
        valor_total=100.00,
        status='COMPLETO'
    )


@pytest.fixture
def tpcccm_especificacao_material_servico(tipo_aplicacao_recurso_custeio, tipo_custeio):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio,
    )


@pytest.fixture
def tpcccm_rateio_despesa(
    associacao,
    tpcccm_despesa,
    conta_associacao_cartao,
    conta_associacao_cheque,
    tipo_aplicacao_recurso_custeio,
    tipo_custeio_servico,
    acao_associacao_ptrf,
    tpcccm_especificacao_material_servico
):
    return baker.make(
        'RateioDespesa',
        despesa=tpcccm_despesa,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        valor_rateio=100.00,
        conferido=True,
        especificacao_material_servico=tpcccm_especificacao_material_servico,
    )


@pytest.fixture
def tpcccm_fechamento_periodo_com_saldo(
    periodo,
    associacao,
    conta_associacao_cheque,
    acao_associacao,
    tpcccm_prestacao_conta
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=20000,
        total_repasses_capital=20000,
        total_despesas_capital=0,
        total_receitas_custeio=20000,
        total_repasses_custeio=20000,
        total_despesas_custeio=0,
        status='FECHADO',
        prestacao_conta=tpcccm_prestacao_conta,
    )


def test_contas_com_movimento_de_gastos(
    tpcccm_prestacao_conta: PrestacaoConta,
    tpcccm_rateio_despesa,
    conta_associacao_cheque,
    conta_associacao_cartao,
):
    contas_com_movimento = tpcccm_prestacao_conta.get_contas_com_movimento()

    assert len(contas_com_movimento) == 1
    assert contas_com_movimento[0] == conta_associacao_cartao


def test_contas_com_movimento_sem_movimento(
    tpcccm_prestacao_conta: PrestacaoConta,
    conta_associacao_cheque,
    conta_associacao_cartao,
):
    contas_com_movimento = tpcccm_prestacao_conta.get_contas_com_movimento()

    assert len(contas_com_movimento) == 0


def test_contas_com_movimento_sem_movimento_mas_com_saldo(
    tpcccm_prestacao_conta: PrestacaoConta,
    conta_associacao_cheque,
    conta_associacao_cartao,
    tpcccm_fechamento_periodo_com_saldo,
):
    contas_com_movimento = tpcccm_prestacao_conta.get_contas_com_movimento(add_sem_movimento_com_saldo=True)

    assert len(contas_com_movimento) == 1
    assert contas_com_movimento[0] == conta_associacao_cheque
