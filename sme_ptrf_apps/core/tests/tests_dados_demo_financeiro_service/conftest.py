import datetime

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models.fechamento_periodo import STATUS_FECHADO
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import (APLICACAO_CAPITAL, APLICACAO_CUSTEIO,
                                                                     APLICACAO_LIVRE)


@pytest.fixture
def df_periodo_2019_2():
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=datetime.date(2019, 7, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 12, 31),
        periodo_anterior=None
    )


@pytest.fixture
def df_periodo_2020_1(df_periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 6, 30),
        periodo_anterior=df_periodo_2019_2
    )


@pytest.fixture
def df_periodo_2020_2(df_periodo_2020_1):
    return baker.make(
        'Periodo',
        referencia='2020.2',
        data_inicio_realizacao_despesas=datetime.date(2020, 7, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 12, 31),
        periodo_anterior=df_periodo_2020_1
    )


@pytest.fixture
def df_periodo_2021_1(df_periodo_2020_2):
    return baker.make(
        'Periodo',
        referencia='2021.1',
        data_inicio_realizacao_despesas=datetime.date(2021, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2021, 6, 30),
        periodo_anterior=df_periodo_2020_2
    )


@pytest.fixture
def df_tipo_conta_cartao():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def df_acao_ptrf():
    return baker.make('Acao', nome='PTRF')


@pytest.fixture
def df_acao_associacao_ptrf(associacao, df_acao_ptrf):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=df_acao_ptrf
    )


@pytest.fixture
def df_conta_associacao_cartao(associacao, df_tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=df_tipo_conta_cartao
    )


@pytest.fixture
def df_tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)


@pytest.fixture
def df_receita_2020_1_cartao_ptrf_repasse_capital_conferida_em_2020_1(
    associacao,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    df_tipo_receita_repasse,
    df_periodo_2020_1,
):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        tipo_receita=df_tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=df_periodo_2020_1,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def df_receita_2020_1_cartao_ptrf_repasse_custeio_conferida_em_2020_1(
    associacao,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    tipo_receita_repasse,
    df_periodo_2020_1
):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=df_periodo_2020_1,
        categoria_receita=APLICACAO_CUSTEIO,
    )


@pytest.fixture
def df_receita_2020_1_cartao_ptrf_repasse_livre_conferida_em_2020_1(
    associacao,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    tipo_receita_repasse,
    df_periodo_2020_1
):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=df_periodo_2020_1,
        categoria_receita=APLICACAO_LIVRE,
    )


@pytest.fixture
def df_tipo_custeio_servico():
    return baker.make('TipoCusteio', nome='Servico')


@pytest.fixture
def df_especificacao_instalacao_eletrica(
    tipo_aplicacao_recurso_custeio,
    df_tipo_custeio_servico
):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Instalação elétrica',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=df_tipo_custeio_servico,
    )


@pytest.fixture
def df_despesa_2020_1(
    associacao,
    tipo_documento,
    tipo_transacao,
    df_periodo_2020_1
):
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
def df_rateio_despesa_2020_1_cartao_ptrf_custeio_conferido_em_2020_1(
    associacao,
    df_despesa_2020_1,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    tipo_aplicacao_recurso_custeio,
    df_tipo_custeio_servico,
    df_especificacao_instalacao_eletrica,
    df_periodo_2020_1
):
    return baker.make(
        'RateioDespesa',
        despesa=df_despesa_2020_1,
        associacao=associacao,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=df_tipo_custeio_servico,
        especificacao_material_servico=df_especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=df_periodo_2020_1,
    )


@pytest.fixture
def df_rateio_despesa_2020_1_cartao_ptrf_custeio_conferido_em_2020_2(
    associacao,
    df_despesa_2020_1,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    tipo_aplicacao_recurso_custeio,
    df_tipo_custeio_servico,
    df_especificacao_instalacao_eletrica,
    df_periodo_2020_2
):
    return baker.make(
        'RateioDespesa',
        despesa=df_despesa_2020_1,
        associacao=associacao,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=df_tipo_custeio_servico,
        especificacao_material_servico=df_especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=df_periodo_2020_2,
    )


@pytest.fixture
def df_despesa_2019_2(
    associacao,
    tipo_documento,
    tipo_transacao,
    df_periodo_2019_2
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2019, 12, 1),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 12, 1),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def df_rateio_despesa_2019_2_cartao_ptrf_custeio_nao_conferido(
    associacao,
    df_despesa_2019_2,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    tipo_aplicacao_recurso_custeio,
    df_tipo_custeio_servico,
    df_especificacao_instalacao_eletrica,
):
    return baker.make(
        'RateioDespesa',
        despesa=df_despesa_2019_2,
        associacao=associacao,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=df_tipo_custeio_servico,
        especificacao_material_servico=df_especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=False,
    )

@pytest.fixture
def df_rateio_despesa_2019_2_cartao_ptrf_custeio_conferido_em_2020_2(
    associacao,
    df_despesa_2019_2,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    tipo_aplicacao_recurso_custeio,
    df_tipo_custeio_servico,
    df_especificacao_instalacao_eletrica,
    df_periodo_2020_2,
):
    return baker.make(
        'RateioDespesa',
        despesa=df_despesa_2019_2,
        associacao=associacao,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=df_tipo_custeio_servico,
        especificacao_material_servico=df_especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=df_periodo_2020_2,
    )


@pytest.fixture
def df_rateio_despesa_2019_2_cartao_ptrf_custeio_conferido_em_2021_1(
    associacao,
    df_despesa_2019_2,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    tipo_aplicacao_recurso_custeio,
    df_tipo_custeio_servico,
    df_especificacao_instalacao_eletrica,
    df_periodo_2021_1,
):
    return baker.make(
        'RateioDespesa',
        despesa=df_despesa_2019_2,
        associacao=associacao,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=df_tipo_custeio_servico,
        especificacao_material_servico=df_especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=df_periodo_2021_1,
    )

@pytest.fixture
def df_prestacao_conta_2020_1(df_periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=df_periodo_2020_1,
        associacao=associacao,
    )


@pytest.fixture
def df_fechamento_periodo_2020_1(
    df_periodo_2020_1,
    associacao,
    df_conta_associacao_cartao,
    df_acao_associacao_ptrf,
    df_prestacao_conta_2020_1
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=df_periodo_2020_1,
        associacao=associacao,
        conta_associacao=df_conta_associacao_cartao,
        acao_associacao=df_acao_associacao_ptrf,
        fechamento_anterior=None,
        total_receitas_custeio=100,
        total_repasses_custeio=100,
        total_despesas_custeio=100,
        status=STATUS_FECHADO,
        prestacao_conta=df_prestacao_conta_2020_1
    )
