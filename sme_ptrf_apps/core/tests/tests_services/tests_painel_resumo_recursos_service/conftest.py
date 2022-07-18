import pytest

from datetime import date

from model_bakery import baker


@pytest.fixture
def prr_periodo_2019_1():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 6, 30),
    )


@pytest.fixture
def prr_periodo_2019_2(prr_periodo_2019_1):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 7, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
        periodo_anterior=prr_periodo_2019_1,
    )


@pytest.fixture
def prr_periodo_2020_1(prr_periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        periodo_anterior=prr_periodo_2019_2,
    )


@pytest.fixture
def prr_periodo_2020_2(prr_periodo_2020_1):
    return baker.make(
        'Periodo',
        referencia='2020.2',
        data_inicio_realizacao_despesas=date(2020, 7, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        periodo_anterior=prr_periodo_2020_1,
    )


@pytest.fixture
def prr_periodo_2021_1(prr_periodo_2020_2):
    return baker.make(
        'Periodo',
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        periodo_anterior=prr_periodo_2020_2,
    )


@pytest.fixture
def prr_associacao(unidade, prr_periodo_2019_1):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        unidade=unidade,
        periodo_inicial=prr_periodo_2019_1,
    )


@pytest.fixture
def prr_conta_associacao_cheque(prr_associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=prr_associacao,
        tipo_conta=tipo_conta_cheque
    )


@pytest.fixture
def prr_conta_associacao_cartao(prr_associacao, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=prr_associacao,
        tipo_conta=tipo_conta_cartao
    )


@pytest.fixture
def prr_acao_associacao_ptrf(prr_associacao, acao_ptrf):
    return baker.make(
        'AcaoAssociacao',
        associacao=prr_associacao,
        acao=acao_ptrf
    )

@pytest.fixture
def prr_acao_associacao_role(prr_associacao, acao_role_cultural):
    return baker.make(
        'AcaoAssociacao',
        associacao=prr_associacao,
        acao=acao_role_cultural
    )


@pytest.fixture
def prr_receita_110_2020_1_ptrf_cheque_custeio(prr_associacao, prr_conta_associacao_cheque, prr_acao_associacao_ptrf, tipo_receita, prr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=prr_associacao,
        data=date(2020, 1, 1),
        valor=110.00,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def prr_receita_110_2020_1_ptrf_cheque_custeio_repasse(prr_associacao, prr_conta_associacao_cheque, prr_acao_associacao_ptrf, tipo_receita_repasse, prr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=prr_associacao,
        data=date(2020, 1, 1),
        valor=110.00,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        categoria_receita='CUSTEIO'
    )




@pytest.fixture
def prr_receita_220_2020_1_ptrf_cheque_capital(prr_associacao, prr_conta_associacao_cheque, prr_acao_associacao_ptrf, tipo_receita, prr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=prr_associacao,
        data=date(2020, 3, 1),
        valor=220.00,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CAPITAL'
    )


@pytest.fixture
def prr_receita_300_2020_1_ptrf_cheque_livre(prr_associacao, prr_conta_associacao_cheque, prr_acao_associacao_ptrf, tipo_receita, prr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=prr_associacao,
        data=date(2020, 3, 1),
        valor=300.00,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='LIVRE'
    )


@pytest.fixture
def prr_receita_400_2020_1_ptrf_cartao_custeio(prr_associacao, prr_conta_associacao_cartao, prr_acao_associacao_ptrf, tipo_receita, prr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=prr_associacao,
        data=date(2020, 1, 1),
        valor=400.00,
        conta_associacao=prr_conta_associacao_cartao,
        acao_associacao=prr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def prr_receita_500_2020_1_role_cheque_custeio(prr_associacao, prr_conta_associacao_cheque, prr_acao_associacao_role, tipo_receita, prr_periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=prr_associacao,
        data=date(2020, 3, 1),
        valor=500.00,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_role,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def prr_receita_650_2020_2_ptrf_cheque_custeio(prr_associacao, prr_conta_associacao_cheque, prr_acao_associacao_ptrf, tipo_receita, prr_periodo_2020_2):
    return baker.make(
        'Receita',
        associacao=prr_associacao,
        data=date(2020, 7, 1),
        valor=650.00,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def prr_despesa_2020_1(prr_associacao, tipo_documento, tipo_transacao, prr_periodo_2020_1):
    return baker.make(
        'Despesa',
        associacao=prr_associacao,
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
def prr_rateio_100_2020_1_ptrf_cheque_custeio(
    prr_associacao,
    prr_despesa_2020_1,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=prr_despesa_2020_1,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00
    )


@pytest.fixture
def prr_rateio_200_2020_1_ptrf_cheque_capital(
    prr_associacao,
    prr_despesa_2020_1,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=prr_despesa_2020_1,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        aplicacao_recurso='CAPITAL',
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=200.00,
        quantidade_itens_capital=2,
        valor_item_capital=100.00,
        numero_processo_incorporacao_capital='Teste654321'
    )


@pytest.fixture
def prr_rateio_300_2020_1_ptrf_cartao_custeio(
    prr_associacao,
    prr_despesa_2020_1,
    prr_conta_associacao_cartao,
    prr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=prr_despesa_2020_1,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cartao,
        acao_associacao=prr_acao_associacao_ptrf,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=300.00
    )


@pytest.fixture
def prr_rateio_400_2020_1_role_cheque_custeio(
    prr_associacao,
    prr_despesa_2020_1,
    prr_conta_associacao_cheque,
    prr_acao_associacao_role,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=prr_despesa_2020_1,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_role,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=400.00
    )


@pytest.fixture
def prr_despesa_2020_2(prr_associacao, tipo_documento, tipo_transacao, prr_periodo_2020_2):
    return baker.make(
        'Despesa',
        associacao=prr_associacao,
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
def prr_rateio_550_2020_2_ptrf_cheque_custeio(
    prr_associacao,
    prr_despesa_2020_2,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    tipo_custeio_material,
    especificacao_material_eletrico,
):
    return baker.make(
        'RateioDespesa',
        despesa=prr_despesa_2020_2,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=550.00
    )


# Fechamentos  =========================================


@pytest.fixture
def prr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550(
    prr_periodo_2019_1,
    prr_associacao,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=prr_periodo_2019_1,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        fechamento_anterior=None,
        total_receitas_capital=220,
        total_despesas_capital=110,
        total_receitas_custeio=440,
        total_despesas_custeio=330,
        total_receitas_livre=550,
    )


@pytest.fixture
def prr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500(
    prr_periodo_2019_2,
    prr_associacao,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    prr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=prr_periodo_2019_2,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        fechamento_anterior=prr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,
        total_receitas_capital=250,
        total_despesas_capital=100,
        total_receitas_custeio=400,
        total_despesas_custeio=300,
        total_receitas_livre=500,
    )


@pytest.fixture
def prr_fechamento_400_2019_2_ptrf_cartao_rcp500_dcp300_rct200_dct100_rlv100(
    prr_periodo_2019_2,
    prr_associacao,
    prr_conta_associacao_cartao,
    prr_acao_associacao_ptrf,
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=prr_periodo_2019_2,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cartao,
        acao_associacao=prr_acao_associacao_ptrf,
        fechamento_anterior=None,
        total_receitas_capital=500,
        total_despesas_capital=300,
        total_receitas_custeio=200,
        total_despesas_custeio=100,
        total_receitas_livre=100,
    )


@pytest.fixture
def prr_fechamento_900_2019_2_role_cheque_rcp300_dcp100_rct500_dct200_rlv400(
    prr_periodo_2019_2,
    prr_associacao,
    prr_conta_associacao_cheque,
    prr_acao_associacao_role,
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=prr_periodo_2019_2,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_role,
        fechamento_anterior=None,
        total_receitas_capital=300,
        total_despesas_capital=100,
        total_receitas_custeio=500,
        total_despesas_custeio=200,
        total_receitas_livre=400,
    )


@pytest.fixture
def prr_fechamento_1820_2020_1_ptrf_cheque_rcp200_dcp200_rct100_dct100_rlv300(
    prr_periodo_2020_1,
    prr_associacao,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    prr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=prr_periodo_2020_1,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        fechamento_anterior=prr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500,
        total_receitas_capital=200,
        total_despesas_capital=200,
        total_receitas_custeio=100,
        total_despesas_custeio=100,
        total_receitas_livre=300,
    )


@pytest.fixture
def prr_fechamento_2600_2020_2_ptrf_cheque_rcp230_dcp120_rct450_dct340_rlv560(
    prr_periodo_2020_2,
    prr_associacao,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    prr_fechamento_1820_2020_1_ptrf_cheque_rcp200_dcp200_rct100_dct100_rlv300,
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=prr_periodo_2020_2,
        associacao=prr_associacao,
        conta_associacao=prr_conta_associacao_cheque,
        acao_associacao=prr_acao_associacao_ptrf,
        fechamento_anterior=prr_fechamento_1820_2020_1_ptrf_cheque_rcp200_dcp200_rct100_dct100_rlv300,
        total_receitas_capital=230,
        total_despesas_capital=120,
        total_receitas_custeio=450,
        total_despesas_custeio=340,
        total_receitas_livre=560,
    )
