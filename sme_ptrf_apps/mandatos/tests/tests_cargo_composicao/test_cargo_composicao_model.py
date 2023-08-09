import pytest
from django.contrib import admin
from ...models import Composicao, CargoComposicao, OcupanteCargo

pytestmark = pytest.mark.django_db


def test_instance_model(
    cargo_composicao_01,
):
    model = cargo_composicao_01
    assert isinstance(model, CargoComposicao)
    assert isinstance(model.composicao, Composicao)
    assert isinstance(model.ocupante_do_cargo, OcupanteCargo)
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert not model.substituto
    assert not model.substituido


def test_str_model(cargo_composicao_01):
    assert cargo_composicao_01.__str__() == "Presidente da diretoria executiva"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[CargoComposicao]
