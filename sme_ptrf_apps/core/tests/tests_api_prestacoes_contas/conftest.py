import datetime

import pytest
from model_bakery import baker


@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)


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
                                       prestacao_conta_iniciada):
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
        conferido=True,
        prestacao_conta=prestacao_conta_iniciada,

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
                                       prestacao_conta_iniciada):
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
        conferido=True,
        prestacao_conta=prestacao_conta_iniciada
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
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_2019_role_conferido_na_prestacao(associacao, despesa_2019_2, conta_associacao_cartao, acao,
                                                    tipo_aplicacao_recurso_custeio,
                                                    tipo_custeio_servico,
                                                    especificacao_cadeira,
                                                    acao_associacao_role_cultural,
                                                    prestacao_conta_iniciada
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
        conferido=True,
        prestacao_conta=prestacao_conta_iniciada,

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
def prestacao_conta_com_analise_anterior(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 10, 1),
        status='RECEBIDA'
    )


@pytest.fixture
def devolucao_prestacao_conta_anterior(prestacao_conta_com_analise_anterior):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_com_analise_anterior,
        data=datetime.date(2020, 7, 1),
        data_limite_ue=datetime.date(2020, 8, 1),
    )


@pytest.fixture
def analise_prestacao_conta_anterior(prestacao_conta_com_analise_anterior, devolucao_prestacao_conta_anterior):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_com_analise_anterior,
        devolucao_prestacao_conta=devolucao_prestacao_conta_anterior
    )


@pytest.fixture
def analise_prestacao_conta_outra_pc(prestacao_conta, devolucao_prestacao_conta_anterior):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta,
        devolucao_prestacao_conta=devolucao_prestacao_conta_anterior
    )




@pytest.fixture
def analise_lancamento_despesa_em_analise_anterior(
    analise_prestacao_conta_anterior,
    despesa_2020_1
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_anterior,
        tipo_lancamento='GASTO',
        despesa=despesa_2020_1,
        resultado='CORRETO'
    )


@pytest.fixture
def analise_lancamento_despesa_em_analise_anterior_realizada(
    analise_prestacao_conta_anterior,
    despesa_2020_1
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_anterior,
        tipo_lancamento='GASTO',
        despesa=despesa_2020_1,
        resultado='AJUSTE',
        status_realizacao='REALIZADO',
    )


@pytest.fixture
def analise_lancamento_despesa_em_analise_anterior_pendente(
    analise_prestacao_conta_anterior,
    despesa_2020_1
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_anterior,
        tipo_lancamento='GASTO',
        despesa=despesa_2020_1,
        resultado='AJUSTE',
        status_realizacao='PENDENTE',
    )


@pytest.fixture
def tipo_devolucao_ao_tesouro_teste():
    return baker.make('TipoDevolucaoAoTesouro', nome='Devolução teste')


@pytest.fixture
def devolucao_ao_tesouro_analise_anterior(prestacao_conta_com_analise_anterior, tipo_devolucao_ao_tesouro_teste, despesa_2020_1):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_com_analise_anterior,
        tipo=tipo_devolucao_ao_tesouro_teste,
        data=datetime.date(2020, 7, 1),
        despesa=despesa_2020_1,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
        visao_criacao='DRE'
    )


@pytest.fixture
def solicitacao_acerto_lancamento_devolucao_analise_anterior(
    analise_lancamento_despesa_em_analise_anterior,
    tipo_acerto_lancamento_devolucao,
    devolucao_ao_tesouro_analise_anterior
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_despesa_em_analise_anterior,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=devolucao_ao_tesouro_analise_anterior,
        detalhamento="teste"
    )


@pytest.fixture
def tipo_acerto_lancamento_conciliacao():
    return baker.make('TipoAcertoLancamento', nome='Conciliar', categoria='CONCILIACAO_LANCAMENTO')


@pytest.fixture
def solicitacao_acerto_lancamento_conciliacao_realizado(
    analise_lancamento_despesa_em_analise_anterior_realizada,
    tipo_acerto_lancamento_conciliacao,
    despesa_2020_1,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_despesa_em_analise_anterior_realizada,
        tipo_acerto=tipo_acerto_lancamento_conciliacao,
        detalhamento="Concliacao teste",
        status_realizacao='REALIZADO',
    )


@pytest.fixture
def solicitacao_acerto_lancamento_conciliacao_pendente(
    analise_lancamento_despesa_em_analise_anterior_pendente,
    tipo_acerto_lancamento_conciliacao,
    despesa_2020_1,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_despesa_em_analise_anterior_pendente,
        tipo_acerto=tipo_acerto_lancamento_conciliacao,
        detalhamento="Concliacao teste",
        status_realizacao='PENDENTE',
    )


@pytest.fixture
def tipo_documento_prestacao_conta_declaracao():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Declaração XPTO', documento_por_conta=True)


@pytest.fixture
def analise_documento_prestacao_analise_anterior(
    analise_prestacao_conta_anterior,
    tipo_documento_prestacao_conta_declaracao,
    conta_associacao_cartao,
    conta_associacao_cheque
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_anterior,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_declaracao,
        conta_associacao=conta_associacao_cartao,
        resultado='AJUSTE'
    )


@pytest.fixture
def solicitacao_acerto_documento_analise_anterior(
    analise_documento_prestacao_analise_anterior,
    tipo_acerto_documento_assinatura,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_analise_anterior,
        tipo_acerto=tipo_acerto_documento_assinatura,
    )
