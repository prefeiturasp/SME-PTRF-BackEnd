import pytest

from ....models.prestacao_conta import STATUS_ABERTO
from ....services import concluir_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_atualizada(prestacao_conta_iniciada, acao_associacao_ptrf):

    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid)

    assert prestacao.status == STATUS_ABERTO, "O status deveria continuar como aberto."
    assert prestacao.conciliado, "Deveria ter sido marcada como conciliado."
    assert prestacao.conciliado_em is not None, "Deveria ter gravado a data e hora da última conciliação."


def test_fechamentos_devem_ser_criados_por_acao(prestacao_conta_iniciada,
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


    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid)
    assert prestacao.fechamentos_da_prestacao.count() == 2, "Deveriam ter sido criados dois fechamentos, um por ação."


def test_deve_sumarizar_transacoes_incluindo_nao_conferidas(prestacao_conta_iniciada,
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

    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid)
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


def test_fechamentos_devem_ser_vinculados_a_anteriores(fechamento_periodo_2019_2,
                                                       prestacao_conta_2020_1_iniciada,
                                                       periodo_2019_2,
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
                                                       acao_associacao_ptrf):

    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_2020_1_iniciada.uuid)

    fechamento = prestacao.fechamentos_da_prestacao.first()

    assert fechamento.fechamento_anterior == fechamento_periodo_2019_2, "Deveria apontar para o fechamento anterior."


def test_deve_gravar_lista_de_especificacoes_despesas(prestacao_conta_iniciada,
                                                      periodo_2020_1,
                                                      despesa_2020_1,
                                                      rateio_despesa_2020_role_custeio_conferido,
                                                      rateio_despesa_2020_role_custeio_nao_conferido,
                                                      rateio_despesa_2020_role_capital_conferido,
                                                      despesa_2019_2,
                                                      rateio_despesa_2019_role_conferido,
                                                      ):

    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid)
    assert prestacao.fechamentos_da_prestacao.count() == 1, "Deveriam ter sido criado apenas um fechamento."

    fechamento = prestacao.fechamentos_da_prestacao.first()
    assert fechamento.especificacoes_despesas_capital == ['Ar condicionado', ]
    assert fechamento.especificacoes_despesas_custeio == ['Instalação elétrica', ]


def test_deve_sumarizar_transacoes_considerando_conta(prestacao_conta_iniciada,
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

    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid)
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
