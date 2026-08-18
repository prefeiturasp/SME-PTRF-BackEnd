import pytest
from sme_ptrf_apps.core.fixtures.factories import FiqueDeOlhoFactory
from sme_ptrf_apps.core.models import TipoTextoFiqueDeOlhoChoices


@pytest.fixture
def fique_de_olho_a():
    return FiqueDeOlhoFactory(
        texto="Texto do Fique de Olho A",
        tipo_texto=TipoTextoFiqueDeOlhoChoices.ASSOCIACOES_PRESTACAO_CONTAS.value
    )


@pytest.fixture
def payload_update_fique_de_olho(fique_de_olho_a):
    payload = {
        'texto': 'Texto do Fique de Olho A - Updated',
    }
    return payload
