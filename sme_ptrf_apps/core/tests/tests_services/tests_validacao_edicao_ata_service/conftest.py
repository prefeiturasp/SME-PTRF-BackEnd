import pytest
from datetime import date

from sme_ptrf_apps.core.models import PrestacaoConta


@pytest.fixture
def prestacao_conta_devolvida(prestacao_conta_factory):
    return prestacao_conta_factory(
        status=PrestacaoConta.STATUS_DEVOLVIDA,
        data_recebimento=date(2020, 10, 1),
    )
