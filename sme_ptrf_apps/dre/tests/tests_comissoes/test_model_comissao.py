import pytest

from django.contrib import admin

from ...models import Comissao

pytestmark = pytest.mark.django_db


def test_instance_model(comissao_exame_contas):
    model = comissao_exame_contas
    assert isinstance(model, Comissao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(comissao_exame_contas):
    assert str(comissao_exame_contas) == 'Exame de Contas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Comissao]
