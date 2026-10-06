import pytest

from sme_ptrf_apps.core.fixtures.factories import FiqueDeOlhoFactory
from sme_ptrf_apps.core.models import TipoTextoFiqueDeOlhoChoices


@pytest.fixture
def fique_de_olho(recurso_legado):
    return FiqueDeOlhoFactory(
        texto="Texto do Fique de Olho",
        tipo_texto=TipoTextoFiqueDeOlhoChoices.ASSOCIACOES_PRESTACAO_CONTAS.value,
        recurso=recurso_legado,
    )
