import pytest
from django.contrib import admin
from ...models import AnaliseRegularidadeAssociacao, AnoAnaliseRegularidade
from sme_ptrf_apps.core.models import Associacao

pytestmark = pytest.mark.django_db


def test_instance_model(analise_regularidade_associacao):
    model = analise_regularidade_associacao
    assert isinstance(model, AnaliseRegularidadeAssociacao)
    assert isinstance(model.ano_analise, AnoAnaliseRegularidade)
    assert isinstance(model.associacao, Associacao)
    assert model.status_regularidade
    assert model.criado_em
    assert model.alterado_em


def test_str_model(analise_regularidade_associacao):
    id = analise_regularidade_associacao.id
    assert analise_regularidade_associacao.__str__() == f'Análise:{id} EOL:123456 Ano:2021'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseRegularidadeAssociacao]
