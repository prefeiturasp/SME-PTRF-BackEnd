import pytest

from ...models import Periodo

pytestmark = pytest.mark.django_db

def test_get_periodo_atual(periodo, periodo_anterior):
    assert Periodo.periodo_atual() == periodo

