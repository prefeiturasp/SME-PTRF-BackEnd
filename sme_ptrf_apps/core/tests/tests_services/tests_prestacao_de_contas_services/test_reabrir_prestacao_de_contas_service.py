import pytest

from ....models import PrestacaoConta, FechamentoPeriodo
from ....services import reabrir_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_apagada(prestacao_conta_2020_1_conciliada):
    reaberta = reabrir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_2020_1_conciliada.uuid)

    assert reaberta, 'PC não foi reaberta'
    assert not PrestacaoConta.objects.filter(uuid=prestacao_conta_2020_1_conciliada.uuid).exists(), 'PC não foi apagada'



def test_fechamentos_devem_ser_apagados(prestacao_conta_2020_1_conciliada, fechamento_2020_1):
    reabrir_prestacao_de_contas(prestacao_contas_uuid=prestacao_conta_2020_1_conciliada.uuid)

    assert not FechamentoPeriodo.objects.exists(), "Os fechamentos da prestação deveriam ter sido apagados."
