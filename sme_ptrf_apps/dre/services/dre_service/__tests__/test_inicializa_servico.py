import pytest


from ..dre_service import DreService, DreServiceException
from sme_ptrf_apps.core.models import Unidade

pytestmark = pytest.mark.django_db


def test_pode_inicializar_dre_service(dre_valida):
    dre_service = DreService(dre_valida)
    assert isinstance(dre_service, DreService)
    assert isinstance(dre_service.dre, Unidade)
    assert dre_service.dre == dre_valida


def test_inicializacao_dre_service_exige_passar_uma_dre():
    with pytest.raises(Exception) as e:
        DreService()


def test_inicializacao_dre_service_exige_passar_uma_dre_valida(escola):
    with pytest.raises(DreServiceException) as e:
        DreService(escola)


