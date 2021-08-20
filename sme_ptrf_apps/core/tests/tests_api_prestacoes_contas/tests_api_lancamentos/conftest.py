import datetime

import pytest
from model_bakery import baker


@pytest.fixture
def periodo_2019_2():
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=datetime.date(2019, 7, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 12, 31),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_2020_1(periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 6, 30),
        periodo_anterior=periodo_2019_2
    )


@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)


@pytest.fixture
def tipo_receita_outras():
    return baker.make('TipoReceita', nome='Outras')


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
def especificacao_cadeira(tipo_aplicacao_recurso_custeio, tipo_custeio_servico):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Cadeira',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
    )


@pytest.fixture
def receita_2020_1_role_repasse_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                          tipo_receita_repasse, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
    )


@pytest.fixture
def receita_2020_1_role_repasse_cheque_conferida(associacao, conta_associacao_cheque, acao_associacao_role_cultural,
                                                 tipo_receita_repasse, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
    )


@pytest.fixture
def receita_2020_1_role_outras_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                         tipo_receita_outras, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_outras,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
    )


@pytest.fixture
def receita_2020_1_role_repasse_nao_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                              tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=False,
        periodo_conciliacao=None,
    )


@pytest.fixture
def receita_2020_1_role_outras_nao_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                             tipo_receita_outras):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_outras,
        update_conferido=True,
        conferido=False,
        periodo_conciliacao=None,
    )


@pytest.fixture
def receita_2020_1_ptrf_repasse_conferida(associacao, conta_associacao_cartao, acao_associacao_ptrf,
                                          tipo_receita_repasse, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
    )


@pytest.fixture
def receita_2020_1_ptrf_repasse_nao_conferida(associacao, conta_associacao_cartao, acao_associacao_ptrf,
                                              tipo_receita_repasse, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=False,
        periodo_conciliacao=periodo_2020_1,
    )


@pytest.fixture
def receita_2019_2_role_repasse_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                          tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2019, 7, 10),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
    )


@pytest.fixture
def receita_2019_2_role_repasse_conferida_no_periodo(associacao, conta_associacao_cartao,
                                                     acao_associacao_role_cultural,
                                                     tipo_receita_repasse, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2019, 7, 10),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
    )


@pytest.fixture
def receita_2019_2_role_repasse_nao_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                              tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2019, 7, 10),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=False,
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
def rateio_despesa_2020_role_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
                                       tipo_aplicacao_recurso_custeio,
                                       tipo_custeio_servico,
                                       especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                       periodo_2020_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,

    )


@pytest.fixture
def rateio_despesa_2020_role_cheque_conferido(associacao, despesa_2020_1, conta_associacao_cheque, acao,
                                              tipo_aplicacao_recurso_custeio,
                                              tipo_custeio_servico,
                                              especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_2020_role_nao_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
                                           tipo_aplicacao_recurso_custeio,
                                           tipo_custeio_servico,
                                           especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=False,

    )


@pytest.fixture
def rateio_despesa_2020_ptrf_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
                                       tipo_aplicacao_recurso_custeio,
                                       tipo_custeio_servico,
                                       especificacao_instalacao_eletrica, acao_associacao_ptrf,
                                       periodo_2020_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1
    )


@pytest.fixture
def rateio_despesa_2020_ptrf_nao_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
                                           tipo_aplicacao_recurso_custeio,
                                           tipo_custeio_servico,
                                           especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=False,

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
def rateio_despesa_2019_role_conferido(associacao, despesa_2019_2, conta_associacao_cartao, acao,
                                       tipo_aplicacao_recurso_custeio,
                                       tipo_custeio_servico,
                                       especificacao_cadeira, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_cadeira,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_2019_role_conferido_no_periodo(associacao, despesa_2019_2, conta_associacao_cartao, acao,
                                                  tipo_aplicacao_recurso_custeio,
                                                  tipo_custeio_servico,
                                                  especificacao_cadeira,
                                                  acao_associacao_role_cultural,
                                                  periodo_2020_1
                                                  ):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_cadeira,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,

    )


@pytest.fixture
def rateio_despesa_2019_role_nao_conferido(associacao, despesa_2019_2, conta_associacao_cartao, acao,
                                           tipo_aplicacao_recurso_custeio,
                                           tipo_custeio_servico,
                                           especificacao_cadeira, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_cadeira,
        valor_rateio=100.00,
        conferido=False,

    )


@pytest.fixture
def repasse_2019_2_pendente(associacao, conta_associacao, acao_associacao, periodo_2019_2):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2019_2,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=False,
        realizado_custeio=False
    )


@pytest.fixture
def repasse_2020_1_capital_pendente(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=False,
        realizado_custeio=True
    )


@pytest.fixture
def repasse_2020_1_custeio_pendente(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=True,
        realizado_custeio=False
    )


@pytest.fixture
def repasse_2020_1_pendente(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=False,
        realizado_custeio=False
    )


@pytest.fixture
def repasse_2020_1_realizado(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='REALIZADO',
        realizado_capital=True,
        realizado_custeio=True
    )


@pytest.fixture
def fechamento_periodo_2019_2_1000(periodo_2019_2, associacao, conta_associacao_cartao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        status='FECHADO'
    )


@pytest.fixture
def fechamento_periodo_2019_2_role_1000(periodo_2019_2, associacao, conta_associacao_cartao,
                                        acao_associacao_role_cultural):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        status='FECHADO'
    )


@pytest.fixture
def prestacao_conta_2020_1_em_analise(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 10, 1),
        status="EM_ANALISE"
    )
