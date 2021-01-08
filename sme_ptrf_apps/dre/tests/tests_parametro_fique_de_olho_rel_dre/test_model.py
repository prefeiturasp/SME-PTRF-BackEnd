import pytest
from model_bakery import baker

from ...models import ParametroFiqueDeOlhoRelDre

pytestmark = pytest.mark.django_db


@pytest.fixture
def parametro_fique_de_olho_rel_dre_abc():
    return baker.make(
        'ParametroFiqueDeOlhoRelDre',
        fique_de_olho='abc',
    )


def test_parametro_fique_de_olho_rel_dre_model(parametro_fique_de_olho_rel_dre_abc):
    assert isinstance(parametro_fique_de_olho_rel_dre_abc, ParametroFiqueDeOlhoRelDre)
    assert parametro_fique_de_olho_rel_dre_abc.fique_de_olho == 'abc'

