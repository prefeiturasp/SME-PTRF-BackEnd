import datetime

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models.fechamento_periodo import STATUS_FECHADO
from sme_ptrf_apps.core.models.prestacao_conta import STATUS_ABERTO
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO


@pytest.fixture
def periodo_2019_2():
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=datetime.date(2019, 9, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 11, 30),
        data_prevista_repasse=datetime.date(2019, 10, 1),
        data_inicio_prestacao_contas=datetime.date(2019, 12, 1),
        data_fim_prestacao_contas=datetime.date(2019, 12, 5),
        periodo_anterior=None
    )

@pytest.fixture
def periodo_2020_1(periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 6, 30),
        data_prevista_repasse=datetime.date(2020, 1, 1),
        data_inicio_prestacao_contas=datetime.date(2020, 7, 1),
        data_fim_prestacao_contas=datetime.date(2020, 7, 10),
        periodo_anterior=periodo_2019_2
    )

@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)


@pytest.fixture
def tipo_receita_rendimento():
    return baker.make('TipoReceita', nome='Rendimento', e_repasse=False)


@pytest.fixture
def receita_2020_1_role_repasse_capital_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita Role Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2020_1_role_repasse_custeio_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita Role Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CUSTEIO,
    )


@pytest.fixture
def receita_2020_1_role_repasse_capital_nao_conferida(associacao, conta_associacao_cartao,
                                                      acao_associacao_role_cultural,
                                                      tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita Role Não Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=False,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2020_1_ptrf_repasse_capital_conferida(associacao, conta_associacao_cartao, acao_associacao_ptrf,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita PTRF Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2019_2_role_repasse_capital_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2019, 7, 10),
        valor=100.00,
        descricao="Receita Role Conferida 2019",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2020_1_role_rendimento_custeio_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                     tipo_receita_rendimento):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita Role Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_rendimento,
        conferido=True,
        categoria_receita=APLICACAO_CUSTEIO,
    )


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
        conferido=True,

    )

@pytest.fixture
def rateio_despesa_2020_role_capital_conferido(associacao, despesa_2020_1, conta_associacao, acao,
                                               tipo_aplicacao_recurso_capital,
                                               tipo_custeio_servico,
                                               especificacao_ar_condicionado, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=100.00,
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
        conferido=True,

    )

@pytest.fixture
def fechamento_periodo_2019_2(periodo_2019_2, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=500,
        total_repasses_capital=450,
        total_despesas_capital=400,
        total_receitas_custeio=1000,
        total_repasses_custeio=900,
        total_despesas_custeio=800,
        status=STATUS_FECHADO
    )

@pytest.fixture
def prestacao_conta_2020_1_iniciada(periodo_2020_1, associacao, conta_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        status=STATUS_ABERTO,
        conciliado=False,
        conciliado_em=None,
        motivo_reabertura=''
    )


@pytest.fixture
def prestacao_conta_2020_1_conciliada(periodo_2020_1, associacao, conta_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        status=STATUS_ABERTO,
        conciliado=True,
        conciliado_em=datetime.date(2020, 7, 1),
        motivo_reabertura=''
    )

@pytest.fixture
def prestacao_conta_2020_1_nao_conciliada(periodo_2020_1, associacao, conta_associacao_cartao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        status=STATUS_ABERTO,
        conciliado=False,
        conciliado_em=None,
        motivo_reabertura=''
    )
