import datetime

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models.fechamento_periodo import STATUS_FECHADO
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import (APLICACAO_CAPITAL, APLICACAO_CUSTEIO,
                                                                     APLICACAO_LIVRE)


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
def periodo_2022_1(periodo_2019_2):
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
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
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
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
        conferido=True,
        categoria_receita=APLICACAO_CUSTEIO,
    )


@pytest.fixture
def receita_2020_1_role_repasse_livre_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
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
        conferido=True,
        categoria_receita=APLICACAO_LIVRE,
    )


@pytest.fixture
def receita_2020_1_role_repasse_custeio_conferida_outra_conta(associacao, conta_associacao_cheque,
                                                              acao_associacao_role_cultural,
                                                              tipo_receita_repasse):
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
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
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
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
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
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        update_conferido=True,
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
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_rendimento,
        update_conferido=True,
        conferido=True,
        categoria_receita=APLICACAO_CUSTEIO,
    )


@pytest.fixture
def receita_2020_1_role_rendimento_livre_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                   tipo_receita_rendimento):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_rendimento,
        update_conferido=True,
        conferido=True,
        categoria_receita=APLICACAO_LIVRE,
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
def rateio_despesa_2020_role_custeio_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
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
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_2020_role_custeio_conferido_outra_conta(associacao, despesa_2020_1, conta_associacao_cheque, acao,
                                                           tipo_aplicacao_recurso_custeio,
                                                           tipo_custeio_servico,
                                                           especificacao_instalacao_eletrica,
                                                           acao_associacao_role_cultural):
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
def rateio_despesa_2020_role_capital_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
                                               tipo_aplicacao_recurso_capital,
                                               tipo_custeio_servico,
                                               especificacao_ar_condicionado, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,
        quantidade_itens_capital=1,
        valor_item_capital=100.0,
        numero_processo_incorporacao_capital="123456"

    )


@pytest.fixture
def rateio_despesa_2020_role_custeio_nao_conferido(associacao, despesa_2020_1, conta_associacao_cartao, acao,
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
        periodo_conciliacao=periodo_2020_1,
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
                                       especificacao_instalacao_eletrica, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
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
def prestacao_conta_2020_1_iniciada(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
    )


@pytest.fixture
def prestacao_conta_2020_1_conciliada(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
    )


@pytest.fixture
def prestacao_conta_2020_1_nao_conciliada(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
    )


@pytest.fixture
def ata_2020_1_teste(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'Ata',
        arquivo_pdf=None,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        periodo=prestacao_conta_2020_1_conciliada.periodo,
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        status_geracao_pdf='NAO_GERADO',
        data_reuniao=datetime.date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        parecer_conselho='APROVADA',
    )


@pytest.fixture
def ata_2022_2_teste_valido(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'Ata',
        arquivo_pdf=None,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        periodo=prestacao_conta_2020_1_conciliada.periodo,
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        status_geracao_pdf='NAO_GERADO',
        data_reuniao=datetime.date(2022, 7, 2),
        local_reuniao='Escola Teste',
        presidente_reuniao='Arnaldo',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Falcao',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        justificativa_repasses_pendentes='teste justificativa',
        parecer_conselho='APROVADA',
    )


@pytest.fixture
def presente_ata_membro_arnaldo(ata_2022_2_teste_valido):
    return baker.make(
        'PresenteAta',
        ata=ata_2022_2_teste_valido,
        identificacao="0001",
        nome="Arnaldo",
        cargo="Presidente",
        membro=True,
        conselho_fiscal=False
    )


@pytest.fixture
def presente_ata_membro_falcao(ata_2022_2_teste_valido):
    return baker.make(
        'PresenteAta',
        ata=ata_2022_2_teste_valido,
        identificacao="0001",
        nome="Falcao",
        cargo="Secretario",
        membro=True,
        conselho_fiscal=False
    )


@pytest.fixture
def ata_2022_test_campos_invalidos(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'Ata',
        arquivo_pdf=None,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        periodo=prestacao_conta_2020_1_conciliada.periodo,
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        status_geracao_pdf='NAO_GERADO',
        data_reuniao=datetime.date(2022, 7, 2),
        local_reuniao='',
        presidente_reuniao='',
        cargo_presidente_reuniao='',
        secretario_reuniao='',
        cargo_secretaria_reuniao='',
        comentarios='Teste',
        parecer_conselho='APROVADA',
    )
