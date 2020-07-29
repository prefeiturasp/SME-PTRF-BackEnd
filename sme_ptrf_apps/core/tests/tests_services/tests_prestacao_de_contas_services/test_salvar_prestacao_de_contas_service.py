import pytest

from ....models.prestacao_conta import STATUS_ABERTO
from ....services import salvar_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_atualizada(prestacao_conta_iniciada, acao_associacao_ptrf):
    observacoes = [{
        "acao_associacao_uuid": str(acao_associacao_ptrf.uuid),
        "observacao": "Teste"
    }]
    prestacao = salvar_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid,
                                           observacoes=observacoes)

    assert prestacao.status == STATUS_ABERTO, "O status deveria continuar como aberto."
    assert not prestacao.conciliado, "Não deveria ter sido marcada como conciliado."
    assert prestacao.conciliado_em is None, "Não deveria ter gravado a data e hora da última conciliação."


def test_fechamentos_nao_devem_ser_criados_por_acao(prestacao_conta_iniciada,
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
                                                    rateio_despesa_2019_role_conferido):
    observacoes = [{
        "acao_associacao_uuid": str(prestacao_conta_iniciada.associacao.acoes.filter(status='ATIVA').first().uuid),
        "observacao": "Teste"
    }]
    prestacao = salvar_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid,
                                           observacoes=observacoes)
    assert prestacao.fechamentos_da_prestacao.count() == 0, "Não deveriam ter sido criados fechamentos."

