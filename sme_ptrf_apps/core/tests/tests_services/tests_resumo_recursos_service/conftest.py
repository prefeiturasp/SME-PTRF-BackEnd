import pytest

from datetime import date

from model_bakery import baker


@pytest.fixture
def rr_periodo_2019_2():
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 7, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
    )


@pytest.fixture
def rr_periodo_2020_1(rr_periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        periodo_anterior=rr_periodo_2019_2,
    )


@pytest.fixture
def rr_periodo_2020_2(rr_periodo_2020_1):
    return baker.make(
        'Periodo',
        referencia='2020.2',
        data_inicio_realizacao_despesas=date(2020, 7, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        periodo_anterior=rr_periodo_2020_1,
    )


@pytest.fixture
def rr_periodo_2021_1(rr_periodo_2020_2):
    return baker.make(
        'Periodo',
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        periodo_anterior=rr_periodo_2020_2,
    )


@pytest.fixture
def rr_associacao(unidade, rr_periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        unidade=unidade,
        periodo_inicial=rr_periodo_2019_2,
    )


@pytest.fixture
def rr_conta_associacao_cheque(rr_associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=rr_associacao,
        tipo_conta=tipo_conta_cheque
    )


@pytest.fixture
def rr_conta_associacao_cartao(rr_associacao, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=rr_associacao,
        tipo_conta=tipo_conta_cartao
    )


@pytest.fixture
def rr_acao_associacao_ptrf(rr_associacao, acao_ptrf):
    return baker.make(
        'AcaoAssociacao',
        associacao=rr_associacao,
        acao=acao_ptrf
    )

@pytest.fixture
def rr_acao_associacao_role(rr_associacao, acao_role_cultural):
    return baker.make(
        'AcaoAssociacao',
        associacao=rr_associacao,
        acao=acao_role_cultural
    )


@pytest.fixture
def rr_receita_100_2020_1_ptrf_cheque_custeio(rr_associacao, rr_conta_associacao_cheque, rr_acao_associacao_ptrf, tipo_receita, rr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=rr_associacao,
        data=date(2020, 1, 1),
        valor=100.00,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def rr_receita_200_2020_1_ptrf_cheque_capital(rr_associacao, rr_conta_associacao_cheque, rr_acao_associacao_ptrf, tipo_receita, rr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=rr_associacao,
        data=date(2020, 3, 1),
        valor=200.00,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CAPITAL'
    )


@pytest.fixture
def rr_receita_300_2020_1_ptrf_cheque_livre(rr_associacao, rr_conta_associacao_cheque, rr_acao_associacao_ptrf, tipo_receita, rr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=rr_associacao,
        data=date(2020, 3, 1),
        valor=300.00,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='LIVRE'
    )


@pytest.fixture
def rr_receita_400_2020_1_ptrf_cartao_custeio(rr_associacao, rr_conta_associacao_cartao, rr_acao_associacao_ptrf, tipo_receita, rr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=rr_associacao,
        data=date(2020, 1, 1),
        valor=400.00,
        conta_associacao=rr_conta_associacao_cartao,
        acao_associacao=rr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def rr_receita_500_2020_1_role_cheque_custeio(rr_associacao, rr_conta_associacao_cheque, rr_acao_associacao_role, tipo_receita, rr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=rr_associacao,
        data=date(2020, 3, 1),
        valor=500.00,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_role,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def rr_receita_650_2020_2_ptrf_cheque_custeio(rr_associacao, rr_conta_associacao_cheque, rr_acao_associacao_ptrf, tipo_receita, rr_periodo_2020_2):
    return baker.make(
        'Receita',
        associacao=rr_associacao,
        data=date(2020, 7, 1),
        valor=650.00,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def rr_despesa_2020_1(rr_associacao, tipo_documento, tipo_transacao, rr_periodo_2020_1):
    return baker.make(
        'Despesa',
        associacao=rr_associacao,
        numero_documento='123456',
        data_documento=date(2020, 1, 1),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 1, 1),
        valor_total=1000.00,
    )


@pytest.fixture
def rr_rateio_100_2020_1_ptrf_cheque_custeio(
    rr_associacao,
    rr_despesa_2020_1,
    rr_conta_associacao_cheque,
    rr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=rr_despesa_2020_1,
        associacao=rr_associacao,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_ptrf,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00
    )


@pytest.fixture
def rr_rateio_200_2020_1_ptrf_cheque_capital(
    rr_associacao,
    rr_despesa_2020_1,
    rr_conta_associacao_cheque,
    rr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=rr_despesa_2020_1,
        associacao=rr_associacao,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_ptrf,
        aplicacao_recurso='CAPITAL',
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=200.00,
        quantidade_itens_capital=2,
        valor_item_capital=100.00,
        numero_processo_incorporacao_capital='Teste654321'
    )


@pytest.fixture
def rr_rateio_300_2020_1_ptrf_cartao_custeio(
    rr_associacao,
    rr_despesa_2020_1,
    rr_conta_associacao_cartao,
    rr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=rr_despesa_2020_1,
        associacao=rr_associacao,
        conta_associacao=rr_conta_associacao_cartao,
        acao_associacao=rr_acao_associacao_ptrf,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=300.00
    )


@pytest.fixture
def rr_rateio_400_2020_1_role_cheque_custeio(
    rr_associacao,
    rr_despesa_2020_1,
    rr_conta_associacao_cheque,
    rr_acao_associacao_role,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=rr_despesa_2020_1,
        associacao=rr_associacao,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_role,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=400.00
    )


@pytest.fixture
def rr_despesa_2020_2(rr_associacao, tipo_documento, tipo_transacao, rr_periodo_2020_2):
    return baker.make(
        'Despesa',
        associacao=rr_associacao,
        numero_documento='123456',
        data_documento=date(2020, 7, 1),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 7, 1),
        valor_total=550.00,
    )


@pytest.fixture
def rr_rateio_550_2020_2_ptrf_cheque_custeio(
    rr_associacao,
    rr_despesa_2020_2,
    rr_conta_associacao_cheque,
    rr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=rr_despesa_2020_2,
        associacao=rr_associacao,
        conta_associacao=rr_conta_associacao_cheque,
        acao_associacao=rr_acao_associacao_ptrf,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=550.00
    )
