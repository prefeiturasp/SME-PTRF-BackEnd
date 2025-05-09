import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(paa):
    assert str(paa) == f"{paa.periodo_paa.referencia} - {paa.associacao}"
