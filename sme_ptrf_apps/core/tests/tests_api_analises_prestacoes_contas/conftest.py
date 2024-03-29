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
def despesa_2020_1_inativa(associacao, tipo_documento, tipo_transacao):
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
        status="INATIVO",
        data_e_hora_de_inativacao=datetime.datetime(2020, 5, 10, 5, 10, 10),
    )


@pytest.fixture
def tag_teste():
    return baker.make(
        'Tag',
        nome="TESTE",
    )


@pytest.fixture
def rateio_despesa_2020_role_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
                                       tipo_aplicacao_recurso_custeio,
                                       tipo_custeio_servico,
                                       especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                       periodo_2020_1, tag_teste):
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
        tag=tag_teste,

    )


@pytest.fixture
def rateio_despesa_2020_role_conferido_inativa(associacao, despesa_2020_1_inativa, conta_associacao_cartao, acao,
                                       tipo_aplicacao_recurso_custeio,
                                       tipo_custeio_servico,
                                       especificacao_instalacao_eletrica, acao_associacao_role_cultural,
                                       periodo_2020_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1_inativa,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=200.00,
        update_conferido=True,
        conferido=True,
        status="INATIVO",
        periodo_conciliacao=periodo_2020_1,
        tag=None,

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
def rateio_despesa_2020_role_nao_conferido_inativa(associacao, despesa_2020_1_inativa, conta_associacao_cartao, acao,
                                           tipo_aplicacao_recurso_custeio,
                                           tipo_custeio_servico,
                                           especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1_inativa,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        status="INATIVO",
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
def prestacao_conta_2020_1_teste_analises(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 10, 1),
        status="EM_ANALISE"
    )


@pytest.fixture
def prestacao_conta_2020_1_teste_inativa_analises(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 4, 4),
        status="EM_ANALISE"
    )


@pytest.fixture
def devolucao_prestacao_conta_2020_1_teste_analises(prestacao_conta_2020_1_teste_analises):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        data=datetime.date(2020, 10, 5),
        data_limite_ue=datetime.date(2020, 8, 1),
    )

@pytest.fixture
def devolucao_prestacao_conta_2020_1_teste_inativa_analises(prestacao_conta_2020_1_teste_inativa_analises):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_inativa_analises,
        data=datetime.date(2020, 10, 5),
        data_limite_ue=datetime.date(2020, 8, 1),
    )


@pytest.fixture
def analise_prestacao_conta_2020_1_teste_analises(
    prestacao_conta_2020_1_teste_analises,
    devolucao_prestacao_conta_2020_1_teste_analises
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_teste_analises
    )


@pytest.fixture
def analise_prestacao_conta_2020_1_teste_analises_com_falha_geracao_doc_apos_acertos(
    prestacao_conta_2020_1_teste_analises,
    devolucao_prestacao_conta_2020_1_teste_analises
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_teste_analises,
        status_versao_apresentacao_apos_acertos='FALHA_AO_GERAR'
    )

@pytest.fixture
def analise_prestacao_conta_2020_1_teste_inativa_analises(
    prestacao_conta_2020_1_teste_inativa_analises,
    devolucao_prestacao_conta_2020_1_teste_inativa_analises
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_inativa_analises,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_teste_inativa_analises
    )

@pytest.fixture
def analise_prestacao_conta_2020_1_teste_analises_sem_versao(
    prestacao_conta_2020_1_teste_analises,
    devolucao_prestacao_conta_2020_1_teste_analises
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_teste_analises,
        versao="-",
        status_versao='NAO_GERADO'
    )

@pytest.fixture
def analise_prestacao_conta_2020_1_teste_analises_com_versao_rascunho_em_processamento(
    prestacao_conta_2020_1_teste_analises,
    devolucao_prestacao_conta_2020_1_teste_analises
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_teste_analises,
        versao="rascunho",
        status_versao='Em processamento',
    )


@pytest.fixture
def analise_lancamento_receita_prestacao_conta_2020_1_teste_analises(
    analise_prestacao_conta_2020_1_teste_analises,
    receita_2020_1_ptrf_repasse_conferida
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        tipo_lancamento='CREDITO',
        receita=receita_2020_1_ptrf_repasse_conferida,
        resultado='AJUSTE'
    )


@pytest.fixture
def analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises(
    analise_prestacao_conta_2020_1_teste_analises,
    despesa_2020_1
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        tipo_lancamento='GASTO',
        despesa=despesa_2020_1,
        resultado='AJUSTE'
    )


@pytest.fixture
def analise_lancamento_despesa_prestacao_conta_2020_1_teste_inativa_analises(
    analise_prestacao_conta_2020_1_teste_inativa_analises,
    despesa_2020_1_inativa
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_inativa_analises,
        tipo_lancamento='GASTO',
        despesa=despesa_2020_1_inativa,
        resultado='AJUSTE'
    )


@pytest.fixture
def tipo_acerto_lancamento_devolucao():
    return baker.make('TipoAcertoLancamento', nome='Devolução', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_basico():
    return baker.make('TipoAcertoLancamento', nome='Básico', categoria='BASICO')


@pytest.fixture
def tipo_devolucao_ao_tesouro_teste():
    return baker.make('TipoDevolucaoAoTesouro', nome='Devolução teste')


@pytest.fixture
def devolucao_ao_tesouro_parcial_ajuste(prestacao_conta_2020_1_teste_analises, tipo_devolucao_ao_tesouro_teste, despesa_2020_1):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        tipo=tipo_devolucao_ao_tesouro_teste,
        data=datetime.date(2020, 7, 1),
        despesa=despesa_2020_1,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
        visao_criacao='DRE'
    )

@pytest.fixture
def devolucao_ao_tesouro_parcial_ajuste_inativa(prestacao_conta_2020_1_teste_inativa_analises, tipo_devolucao_ao_tesouro_teste, despesa_2020_1_inativa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_2020_1_teste_inativa_analises,
        tipo=tipo_devolucao_ao_tesouro_teste,
        data=datetime.date(2020, 7, 1),
        despesa=despesa_2020_1_inativa,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
        visao_criacao='DRE'
    )

@pytest.fixture
def solicitacao_acerto_lancamento_devolucao_teste_analises(
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
    tipo_acerto_lancamento_devolucao,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste"
    )

@pytest.fixture
def solicitacao_devolucao_ao_tesouro_teste_analises(
    solicitacao_acerto_lancamento_devolucao_teste_analises,
    tipo_devolucao_ao_tesouro_teste,
):
    return baker.make(
        'SolicitacaoDevolucaoAoTesouro',
        solicitacao_acerto_lancamento=solicitacao_acerto_lancamento_devolucao_teste_analises,
        tipo=tipo_devolucao_ao_tesouro_teste,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
    )

@pytest.fixture
def solicitacao_acerto_lancamento_devolucao_teste_inativa_analises(
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_inativa_analises,
    tipo_acerto_lancamento_devolucao,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_despesa_prestacao_conta_2020_1_teste_inativa_analises,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste"
    )

@pytest.fixture
def solicitacao_devolucao_ao_tesouro_teste_inativa_analises(
    solicitacao_acerto_lancamento_devolucao_teste_inativa_analises,
    tipo_devolucao_ao_tesouro_teste,
):
    return baker.make(
        'SolicitacaoDevolucaoAoTesouro',
        solicitacao_acerto_lancamento=solicitacao_acerto_lancamento_devolucao_teste_inativa_analises,
        tipo=tipo_devolucao_ao_tesouro_teste,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
    )



@pytest.fixture
def solicitacao_acerto_lancamento_basico_tipo_teste_analises(
    analise_lancamento_receita_prestacao_conta_2020_1_teste_analises,
    tipo_acerto_lancamento_basico,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1_teste_analises,
        tipo_acerto=tipo_acerto_lancamento_basico,
        devolucao_ao_tesouro=None,
        detalhamento="teste 2"
    )

@pytest.fixture
def tipo_documento_prestacao_conta_declaracao():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Declaração XPTO', documento_por_conta=True)


@pytest.fixture
def tipo_documento_prestacao_conta_ata():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas', documento_por_conta=False)


@pytest.fixture
def analise_documento_prestacao_conta_2020_1_ata_correta(
    analise_prestacao_conta_2020_1_teste_analises,
    tipo_documento_prestacao_conta_ata
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        resultado='CORRETO'
    )


@pytest.fixture
def analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta(
    analise_prestacao_conta_2020_1_teste_analises,
    tipo_documento_prestacao_conta_declaracao,
    conta_associacao_cartao,
    conta_associacao_cheque
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_declaracao,
        conta_associacao=conta_associacao_cartao,
        resultado='CORRETO'
    )


@pytest.fixture
def tipo_conta_carteira():
    return baker.make(
        'TipoConta',
        nome='Carteira',
    )


@pytest.fixture
def tipo_acerto_documento_assinatura(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar com assinatura')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def analise_documento_prestacao_conta_2020_1_ata_ajuste(
    analise_prestacao_conta_2020_1_teste_analises,
    tipo_documento_prestacao_conta_ata,
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        conta_associacao=None,
        resultado='AJUSTE'
    )

@pytest.fixture
def solicitacao_acerto_documento_ata_teste_analises(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_assinatura,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_assinatura,
    )

@pytest.fixture
def analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste(
    analise_prestacao_conta_2020_1_teste_analises,
    tipo_documento_prestacao_conta_declaracao,
    conta_associacao_cartao,
    conta_associacao_cheque
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_analises,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_declaracao,
        conta_associacao=conta_associacao_cartao,
        resultado='AJUSTE'
    )

@pytest.fixture
def solicitacao_acerto_documento_declaracao_cartao_teste_analises(
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste,
    tipo_acerto_documento_assinatura,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste,
        tipo_acerto=tipo_acerto_documento_assinatura,
        detalhamento=''
    )
