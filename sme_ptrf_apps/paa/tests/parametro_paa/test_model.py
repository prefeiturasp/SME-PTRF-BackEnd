import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(parametro_paa):
    assert str(parametro_paa) == 'Parâmetros do PAA'
