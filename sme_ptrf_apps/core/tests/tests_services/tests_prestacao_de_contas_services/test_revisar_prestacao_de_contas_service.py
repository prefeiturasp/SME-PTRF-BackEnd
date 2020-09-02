import pytest

from ....models.prestacao_conta import STATUS_ABERTO
from ....services import reabrir_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_atualizada(prestacao_conta_2020_1_conciliada):
    motivo = "Teste"
    prestacao = reabrir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_2020_1_conciliada.uuid)

    assert prestacao.status == STATUS_ABERTO, "O status deveria ser aberto."


def test_fechamentos_devem_ser_apagados(prestacao_conta_2020_1_conciliada, fechamento_2020_1):
    motivo = "Teste"
    prestacao = reabrir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_2020_1_conciliada.uuid)

    assert prestacao.fechamentos_da_prestacao.count() == 0, "Os fechamentos da prestação deveriam ter sido apagados."
