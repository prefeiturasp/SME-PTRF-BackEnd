import pytest

from ...models.prestacao_conta import STATUS_ABERTO
from ...services import iniciar_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_criada(conta_associacao, periodo):
    prestacao = iniciar_prestacao_de_contas(conta_associacao_uuid=conta_associacao.uuid, periodo_uuid=periodo.uuid)

    assert prestacao.periodo == periodo
    assert prestacao.conta_associacao == conta_associacao
    assert prestacao.status == STATUS_ABERTO

# def test_fechamentos_devem_ser_criados(conta_associacao,
#                                        periodo_2020_1,
#                                        receita_conferida,
#                                        receita_nao_conferida,
#                                        rateio_despesa_conferido,
#                                        rateio_despesa_nao_conferido):
#     prestacao = iniciar_prestacao_de_contas(conta_associacao_uuid=conta_associacao.uuid, periodo_uuid=periodo_2020_1.uuid)
#
#     assert prestacao.fechamentos_da_prestacao.exists()
