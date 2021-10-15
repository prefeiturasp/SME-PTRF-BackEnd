import pytest

from datetime import date

from model_bakery import baker


@pytest.fixture
def dem_fin_periodo_2019_1():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 6, 30),
    )


@pytest.fixture
def dem_fin_periodo_2019_2(dem_fin_periodo_2019_1):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 7, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 1, 1),
        data_fim_prestacao_contas=date(2020, 1, 5),
        periodo_anterior=dem_fin_periodo_2019_1,
    )


@pytest.fixture
def dem_fin_acao_ptrf():
    return baker.make('Acao', nome='PTRF')


@pytest.fixture
def dem_fin_associacao(unidade, dem_fin_periodo_2019_1):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=dem_fin_periodo_2019_1,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def dem_fin_tipo_conta_cheque():
    return baker.make(
        'TipoConta',
        nome='Cheque',
        banco_nome='Banco do Inter',
        agencia='67945',
        numero_conta='935556-x',
        numero_cartao='987644164221'
    )


@pytest.fixture
def dem_fin_conta_associacao_cheque(dem_fin_associacao, dem_fin_tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=dem_fin_associacao,
        tipo_conta=dem_fin_tipo_conta_cheque,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def dem_fin_acao_associacao_ptrf(dem_fin_associacao, dem_fin_acao_ptrf):
    return baker.make(
        'AcaoAssociacao',
        associacao=dem_fin_associacao,
        acao=dem_fin_acao_ptrf
    )


@pytest.fixture
def dem_fin_tipo_receita_estorno():
    return baker.make('TipoReceita', nome='Estorno')


@pytest.fixture
def dem_fin_receita_estorno_100_custeio_conferida(
    dem_fin_periodo_2019_2,
    dem_fin_associacao,
    dem_fin_conta_associacao_cheque,
    dem_fin_acao_associacao_ptrf,
    dem_fin_tipo_receita_estorno,
):
    return baker.make(
        'Receita',
        associacao=dem_fin_associacao,
        data=date(2019, 7, 10),
        valor=356.56,
        conta_associacao=dem_fin_conta_associacao_cheque,
        acao_associacao=dem_fin_acao_associacao_ptrf,
        tipo_receita=dem_fin_tipo_receita_estorno,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=dem_fin_periodo_2019_2,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def dem_fin_receita_custeio_conferida(
    dem_fin_periodo_2019_2,
    dem_fin_associacao,
    dem_fin_conta_associacao_cheque,
    dem_fin_acao_associacao_ptrf,
    dem_fin_tipo_receita_estorno,
):
    return baker.make(
        'Receita',
        associacao=dem_fin_associacao,
        data=date(2019, 7, 10),
        valor=356.56,
        conta_associacao=dem_fin_conta_associacao_cheque,
        acao_associacao=dem_fin_acao_associacao_ptrf,
        tipo_receita=dem_fin_tipo_receita_estorno,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=dem_fin_periodo_2019_2,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def dem_fin_receita_livre_conferida(
    dem_fin_periodo_2019_2,
    dem_fin_associacao,
    dem_fin_conta_associacao_cheque,
    dem_fin_acao_associacao_ptrf,
    dem_fin_tipo_receita_estorno,
):
    return baker.make(
        'Receita',
        associacao=dem_fin_associacao,
        data=date(2019, 7, 10),
        valor=56389.58,
        conta_associacao=dem_fin_conta_associacao_cheque,
        acao_associacao=dem_fin_acao_associacao_ptrf,
        tipo_receita=dem_fin_tipo_receita_estorno,
        conferido=True,
        update_conferido=True,
        periodo_conciliacao=dem_fin_periodo_2019_2,
        categoria_receita='LIVRE'
    )

@pytest.fixture
def dem_fin_despesa(dem_fin_associacao, tipo_documento, tipo_transacao, dem_fin_periodo_2019_2):
    return baker.make(
        'Despesa',
        associacao=dem_fin_associacao,
        numero_documento='123456',
        data_documento=date(2019, 7, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2019, 7, 10),
        valor_total=87186.89,
        valor_recursos_proprios=0,
    )


@pytest.fixture
def dem_fin_tipo_custeio_material():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def dem_fin_especificacao_material_eletrico(dem_fin_tipo_custeio_material):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=dem_fin_tipo_custeio_material,
    )


@pytest.fixture
def dem_fin_rateio_despesa(
    dem_fin_associacao,
    dem_fin_despesa,
    dem_fin_conta_associacao_cheque,
    dem_fin_acao_associacao_ptrf,
    dem_fin_tipo_custeio_material,
    dem_fin_especificacao_material_eletrico
):
    return baker.make(
        'RateioDespesa',
        despesa=dem_fin_despesa,
        associacao=dem_fin_associacao,
        conta_associacao=dem_fin_conta_associacao_cheque,
        acao_associacao=dem_fin_acao_associacao_ptrf,
        aplicacao_recurso='CUSTEIO',
        tipo_custeio=dem_fin_tipo_custeio_material,
        especificacao_material_servico=dem_fin_especificacao_material_eletrico,
        valor_rateio=87186.89,
    )


@pytest.fixture
def dem_fin_observacao_conciliacao_2019_2(dem_fin_periodo_2019_2, dem_fin_conta_associacao_cheque):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=dem_fin_periodo_2019_2,
        associacao=dem_fin_conta_associacao_cheque.associacao,
        conta_associacao=dem_fin_conta_associacao_cheque,
        texto="Uma bela observação.",
        data_extrato=date(2019, 12, 31),
        saldo_extrato=1000
    )


@pytest.fixture
def dem_fin_fechamento_2019_1(
    dem_fin_periodo_2019_1,
    dem_fin_associacao,
    dem_fin_conta_associacao_cheque,
    dem_fin_acao_associacao_ptrf
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=dem_fin_periodo_2019_1,
        associacao=dem_fin_associacao,
        conta_associacao=dem_fin_conta_associacao_cheque,
        acao_associacao=dem_fin_acao_associacao_ptrf,
        fechamento_anterior=None,
        total_receitas_capital=4927.24,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=31285.67,
        total_repasses_custeio=0,
        total_despesas_custeio=0,
        total_receitas_livre=65998.35,
        status='FECHADO'
    )


@pytest.fixture
def dem_fin_prestacao_conta_2019_2(dem_fin_periodo_2019_2, dem_fin_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=dem_fin_periodo_2019_2,
        associacao=dem_fin_associacao,
        data_recebimento=date(2020, 1, 10),
        status='RECEBIDA'
    )


@pytest.fixture
def dem_fin_fechamento_2019_2(
    dem_fin_periodo_2019_2,
    dem_fin_associacao,
    dem_fin_conta_associacao_cheque,
    dem_fin_acao_associacao_ptrf,
    dem_fin_fechamento_2019_1
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=dem_fin_periodo_2019_2,
        associacao=dem_fin_associacao,
        conta_associacao=dem_fin_conta_associacao_cheque,
        acao_associacao=dem_fin_acao_associacao_ptrf,
        fechamento_anterior=dem_fin_fechamento_2019_1,
        total_receitas_capital=0,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=356.56,
        total_repasses_custeio=0,
        total_despesas_custeio=87186.89,
        total_receitas_livre=56389.58,
        total_repasses_livre=0,
        status='FECHADO'
    )
