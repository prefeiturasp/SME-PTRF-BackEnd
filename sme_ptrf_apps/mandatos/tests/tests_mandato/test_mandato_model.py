import pytest
from django.contrib import admin
from ...models import Mandato

pytestmark = pytest.mark.django_db


def test_instance_model(mandato_2023_a_2025):
    model = mandato_2023_a_2025
    assert isinstance(model, Mandato)
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.data_inicial
    assert model.data_final


def test_str_model(mandato_2023_a_2025):
    assert mandato_2023_a_2025.__str__() == '2023 a 2025'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Mandato]
