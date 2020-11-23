import pytest
from django.contrib import admin
from model_bakery import baker

from ...models import Censo

pytestmark = pytest.mark.django_db


@pytest.fixture
def censo(unidade):
    return baker.make(
        'Censo',
        unidade=unidade,
        quantidade_alunos=35,
        ano='2020'
    )


def test_model_censo(censo):
    model = censo
    assert model.unidade
    assert model.quantidade_alunos
    assert model.ano


def test_censo_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Censo]
