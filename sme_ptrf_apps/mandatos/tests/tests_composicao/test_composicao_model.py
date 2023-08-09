import pytest
from django.contrib import admin
from ...models import Mandato, Composicao

pytestmark = pytest.mark.django_db


def test_instance_model(
    composicao_01_2023_a_2025,
):
    model = composicao_01_2023_a_2025
    assert isinstance(model, Composicao)
    assert isinstance(model.mandato, Mandato)
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.data_inicial
    assert model.data_final


def test_str_model(composicao_01_2023_a_2025):
    assert composicao_01_2023_a_2025.__str__() == "Escola Teste Período 01/01/2023 até 31/12/2025"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Composicao]
