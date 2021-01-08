import pytest

from ...models import ParametroFiqueDeOlhoPc

pytestmark = pytest.mark.django_db


def test_parametro_fique_de_olho_pc_model(parametro_fique_de_olho_pc):
    assert isinstance(parametro_fique_de_olho_pc, ParametroFiqueDeOlhoPc)
    assert parametro_fique_de_olho_pc.fique_de_olho == ''

