import datetime

import pytest
from model_bakery import baker


@pytest.fixture
def tipo_custeio_servico():
    return baker.make('TipoCusteio', nome='Servico')


@pytest.fixture
def especificacao_instalacao_eletrica(tipo_aplicacao_recurso_custeio, tipo_custeio_servico):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Instalação elétrica',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
    )


@pytest.fixture
def despesa_2020_1(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_2020_role_custeio_conferido(associacao, despesa_2020_1, conta_associacao, acao,
                                               tipo_aplicacao_recurso_custeio,
                                               tipo_custeio_servico,
                                               especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_2020_role_capital_conferido(associacao, despesa_2020_1, conta_associacao, acao,
                                               tipo_aplicacao_recurso_capital,
                                               tipo_custeio_servico,
                                               especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_2020_role_custeio_nao_conferido(associacao, despesa_2020_1, conta_associacao, acao,
                                                   tipo_aplicacao_recurso_custeio,
                                                   tipo_custeio_servico,
                                                   especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=False,

    )


@pytest.fixture
def rateio_despesa_2020_ptrf_conferido(associacao, despesa_2020_1, conta_associacao, acao,
                                       tipo_aplicacao_recurso_custeio,
                                       tipo_custeio_servico,
                                       especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def despesa_2019_2(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2019, 6, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 6, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_2019_role_conferido(associacao, despesa_2019_2, conta_associacao, acao,
                                       tipo_aplicacao_recurso_custeio,
                                       tipo_custeio_servico,
                                       especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def despesa_01_03_2020(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 1),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2020, 3, 1),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_01_03_2020_conferido(associacao, despesa_01_03_2020, conta_associacao, acao,
                                        tipo_aplicacao_recurso_custeio,
                                        tipo_custeio_servico,
                                        especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_01_03_2020,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
    )


@pytest.fixture
def rateio_despesa_01_03_2020_nao_conferido(associacao, despesa_01_03_2020, conta_associacao, acao,
                                            tipo_aplicacao_recurso_custeio,
                                            tipo_custeio_servico,
                                            especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_01_03_2020,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=False,
    )
