import pytest
from django.contrib import admin
from ...models import AnoAnaliseRegularidade

pytestmark = pytest.mark.django_db


def test_instance_model(ano_analise_regularidade_2021):
    model = ano_analise_regularidade_2021
    assert isinstance(model, AnoAnaliseRegularidade)
    assert model.ano
    assert model.criado_em
    assert model.alterado_em
    assert model.atualizacao_em_massa is False
    assert model.status_atualizacao


def test_str_model(ano_analise_regularidade_2021):
    assert ano_analise_regularidade_2021.__str__() == '2021'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnoAnaliseRegularidade]
