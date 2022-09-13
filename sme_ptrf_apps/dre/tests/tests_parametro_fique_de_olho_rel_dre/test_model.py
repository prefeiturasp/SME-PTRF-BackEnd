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


def test_audit_log(parametro_fique_de_olho_rel_dre_abc):
    assert parametro_fique_de_olho_rel_dre_abc.history.count() == 1  # Um log de inclusão
    assert parametro_fique_de_olho_rel_dre_abc.history.latest().action == 0  # 0-Inclusão

    parametro_fique_de_olho_rel_dre_abc.fique_de_olho = "teste"
    parametro_fique_de_olho_rel_dre_abc.save()
    assert parametro_fique_de_olho_rel_dre_abc.history.count() == 2  # Um log de inclusão e outro de edição
    assert parametro_fique_de_olho_rel_dre_abc.history.latest().action == 1  # 1-Edição

