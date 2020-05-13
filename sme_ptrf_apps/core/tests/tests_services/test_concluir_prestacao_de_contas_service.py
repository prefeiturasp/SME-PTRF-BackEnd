import pytest

from ...models.prestacao_conta import STATUS_ABERTO
from ...services import concluir_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_atualizada(prestacao_conta_iniciada):
    observacoes = "Teste"
    prestacao = concluir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_iniciada.uuid,
                                             observacoes=observacoes)

    assert prestacao.observacoes == observacoes, "Deveria ter gravado as observações"
    assert prestacao.status == STATUS_ABERTO, "O status deveria continuar como aberto."
    assert prestacao.conciliado, "Deveria ter sido marcada como conciliado."
    assert prestacao.conciliado_em is not None, "Deveria ter gravado a data e hora da última conciliação."

# def test_fechamentos_devem_ser_criados(conta_associacao,
#                                        periodo_2020_1,
#                                        receita_conferida,
#                                        receita_nao_conferida,
#                                        rateio_despesa_conferido,
#                                        rateio_despesa_nao_conferido):
#     prestacao = iniciar_prestacao_de_contas(conta_associacao_uuid=conta_associacao.uuid, periodo_uuid=periodo_2020_1.uuid)
#
#     assert prestacao.fechamentos_da_prestacao.exists()
