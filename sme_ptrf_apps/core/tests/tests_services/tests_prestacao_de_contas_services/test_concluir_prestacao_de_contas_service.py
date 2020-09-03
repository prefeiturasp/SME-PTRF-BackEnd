from datetime import date

import pytest
from model_bakery import baker

from ....models.prestacao_conta import STATUS_FECHADO
from ....services import concluir_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_criada(associacao, periodo):
    prestacao = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo)

    assert prestacao.status == STATUS_FECHADO, "A PC deveria estar fechada."


# TODO Implementar teste para conclusão de PC já ewxistente (Caso de reabertura)
def _test_prestacao_de_contas_deve_ser_atualizada(prestacao_conta_iniciada, acao_associacao_ptrf):
    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid)

    assert prestacao.status == STATUS_ABERTO, "O status deveria continuar como aberto."


def test_fechamentos_devem_ser_criados_por_acao(associacao,
                                                periodo_2020_1,
                                                receita_2020_1_role_repasse_custeio_conferida,
                                                receita_2020_1_ptrf_repasse_capital_conferida,
                                                receita_2020_1_role_repasse_capital_nao_conferida,
                                                receita_2019_2_role_repasse_capital_conferida,
                                                receita_2020_1_role_repasse_capital_conferida,
                                                receita_2020_1_role_rendimento_custeio_conferida,
                                                despesa_2020_1,
                                                rateio_despesa_2020_role_custeio_conferido,
                                                rateio_despesa_2020_role_custeio_nao_conferido,
                                                rateio_despesa_2020_role_capital_conferido,
                                                despesa_2019_2,
                                                rateio_despesa_2019_role_conferido,
                                                acao_associacao_ptrf):
    prestacao = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo_2020_1)
    assert prestacao.fechamentos_da_prestacao.count() == 2, "Deveriam ter sido criados dois fechamentos, um por ação."


def test_deve_sumarizar_transacoes_incluindo_nao_conferidas(associacao,
                                                            periodo_2020_1,
                                                            receita_2020_1_role_repasse_custeio_conferida,
                                                            receita_2020_1_role_repasse_capital_nao_conferida,
                                                            receita_2019_2_role_repasse_capital_conferida,
                                                            receita_2020_1_role_repasse_capital_conferida,
                                                            receita_2020_1_role_rendimento_custeio_conferida,
                                                            despesa_2020_1,
                                                            rateio_despesa_2020_role_custeio_conferido,
                                                            rateio_despesa_2020_role_custeio_nao_conferido,
                                                            rateio_despesa_2020_role_capital_conferido,
                                                            despesa_2019_2,
                                                            rateio_despesa_2019_role_conferido,
                                                            ):
    prestacao = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo_2020_1)
    assert prestacao.fechamentos_da_prestacao.count() == 1, "Deveriam ter sido criado apenas um fechamento."

    fechamento = prestacao.fechamentos_da_prestacao.first()

    total_receitas_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_receitas_capital == total_receitas_capital_esperado
    assert fechamento.total_receitas_nao_conciliadas_capital == receita_2020_1_role_repasse_capital_nao_conferida.valor

    total_repasses_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_repasses_capital == total_repasses_capital_esperado

    total_receitas_custeio_esperado = receita_2020_1_role_rendimento_custeio_conferida.valor + \
                                      receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_receitas_custeio == total_receitas_custeio_esperado
    assert fechamento.total_receitas_nao_conciliadas_custeio == 0

    total_repasses_custeio_esperado = receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_repasses_custeio == total_repasses_custeio_esperado

    total_despesas_capital = rateio_despesa_2020_role_capital_conferido.valor_rateio
    assert fechamento.total_despesas_capital == total_despesas_capital
    assert fechamento.total_despesas_nao_conciliadas_capital == 0

    total_despesas_custeio = rateio_despesa_2020_role_custeio_conferido.valor_rateio + \
                             rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio
    assert fechamento.total_despesas_custeio == total_despesas_custeio
    assert fechamento.total_despesas_nao_conciliadas_custeio == rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio


@pytest.fixture
def _periodo_2019_2(periodo):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 6, 1),
        data_fim_realizacao_despesas=date(2019, 12, 30),
        data_prevista_repasse=date(2019, 6, 1),
        data_inicio_prestacao_contas=date(2020, 1, 1),
        data_fim_prestacao_contas=date(2020, 1, 10),
        periodo_anterior=periodo
    )


@pytest.fixture
def _periodo_2020_1(_periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=_periodo_2019_2
    )


@pytest.fixture
def _fechamento_2019_2(_periodo_2019_2, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=_periodo_2019_2,
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
def _receita_2020_1(associacao, conta_associacao, acao_associacao, tipo_receita_rendimento):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_rendimento,
        conferido=True,
    )


def test_fechamentos_devem_ser_vinculados_a_anteriores(_fechamento_2019_2,
                                                       associacao,
                                                       _periodo_2019_2,
                                                       _periodo_2020_1,
                                                       _receita_2020_1,
                                                       acao_associacao):
    prestacao = concluir_prestacao_de_contas(associacao=associacao, periodo=_periodo_2020_1)

    fechamento = prestacao.fechamentos_da_prestacao.first()

    assert fechamento.fechamento_anterior == _fechamento_2019_2, "Deveria apontar para o fechamento anterior."


def test_deve_gravar_lista_de_especificacoes_despesas(associacao,
                                                      periodo_2020_1,
                                                      despesa_2020_1,
                                                      rateio_despesa_2020_role_custeio_conferido,
                                                      rateio_despesa_2020_role_custeio_nao_conferido,
                                                      rateio_despesa_2020_role_capital_conferido,
                                                      despesa_2019_2,
                                                      rateio_despesa_2019_role_conferido,
                                                      ):
    prestacao = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo_2020_1)
    assert prestacao.fechamentos_da_prestacao.count() == 1, "Deveriam ter sido criado apenas um fechamento."

    fechamento = prestacao.fechamentos_da_prestacao.first()
    assert fechamento.especificacoes_despesas_capital == ['Ar condicionado', ]
    assert fechamento.especificacoes_despesas_custeio == ['Instalação elétrica', ]


def test_deve_sumarizar_transacoes_considerando_conta(associacao,
                                                      conta_associacao_cartao,
                                                      conta_associacao_cheque,
                                                      periodo_2020_1,
                                                      receita_2020_1_role_repasse_custeio_conferida,
                                                      receita_2020_1_role_repasse_capital_nao_conferida,
                                                      receita_2019_2_role_repasse_capital_conferida,
                                                      receita_2020_1_role_repasse_capital_conferida,
                                                      receita_2020_1_role_rendimento_custeio_conferida,
                                                      despesa_2020_1,
                                                      rateio_despesa_2020_role_custeio_conferido,
                                                      rateio_despesa_2020_role_custeio_nao_conferido,
                                                      rateio_despesa_2020_role_capital_conferido,
                                                      despesa_2019_2,
                                                      rateio_despesa_2019_role_conferido,
                                                      receita_2020_1_role_repasse_custeio_conferida_outra_conta,
                                                      rateio_despesa_2020_role_custeio_conferido_outra_conta,
                                                      ):
    prestacao = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo_2020_1)
    assert prestacao.fechamentos_da_prestacao.count() == 2, "Deveriam ter sido criados dois fechamentos."

    fechamento = prestacao.fechamentos_da_prestacao.filter(conta_associacao=conta_associacao_cartao).first()

    total_receitas_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_receitas_capital == total_receitas_capital_esperado
    assert fechamento.total_receitas_nao_conciliadas_capital == receita_2020_1_role_repasse_capital_nao_conferida.valor

    total_repasses_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_repasses_capital == total_repasses_capital_esperado

    total_receitas_custeio_esperado = receita_2020_1_role_rendimento_custeio_conferida.valor + \
                                      receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_receitas_custeio == total_receitas_custeio_esperado
    assert fechamento.total_receitas_nao_conciliadas_custeio == 0

    total_repasses_custeio_esperado = receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_repasses_custeio == total_repasses_custeio_esperado

    total_despesas_capital = rateio_despesa_2020_role_capital_conferido.valor_rateio
    assert fechamento.total_despesas_capital == total_despesas_capital
    assert fechamento.total_despesas_nao_conciliadas_capital == 0

    total_despesas_custeio = rateio_despesa_2020_role_custeio_conferido.valor_rateio + \
                             rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio
    assert fechamento.total_despesas_custeio == total_despesas_custeio
    assert fechamento.total_despesas_nao_conciliadas_custeio == rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio
