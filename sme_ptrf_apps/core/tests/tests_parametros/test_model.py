import pytest

from ...models import Parametros

pytestmark = pytest.mark.django_db


def test_parametros_model(parametros):
    assert isinstance(parametros, Parametros)
    assert parametros.permite_saldo_conta_negativo
