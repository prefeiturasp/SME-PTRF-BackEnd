import pytest
from django.contrib import admin

from ...models import UnidadeEmSuporte,User
from sme_ptrf_apps.core.models import Unidade

pytestmark = pytest.mark.django_db


def test_instance_model(unidade_em_suporte):
    model = unidade_em_suporte
    assert isinstance(model, UnidadeEmSuporte)
    assert model.unidade
    assert isinstance(model.unidade, Unidade)
    assert model.user
    assert isinstance(model.user, User)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(unidade_em_suporte):
    assert unidade_em_suporte.__str__() == f'Unidade 12345 em suporte por 271170. ID:{unidade_em_suporte.id}'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[UnidadeEmSuporte]
