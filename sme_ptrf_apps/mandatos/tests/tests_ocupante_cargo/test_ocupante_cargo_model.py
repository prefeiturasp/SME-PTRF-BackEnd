import pytest
from django.contrib import admin
from ...models import OcupanteCargo

pytestmark = pytest.mark.django_db


def test_instance_model(
    ocupante_cargo_01,
):
    model = ocupante_cargo_01
    assert isinstance(model, OcupanteCargo)
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.nome
    assert model.codigo_identificacao
    assert model.cargo_educacao
    assert model.representacao
    assert model.email
    assert model.cpf_responsavel
    assert model.telefone
    assert model.cep
    assert model.bairro
    assert model.endereco


def test_str_model(ocupante_cargo_01):
    assert ocupante_cargo_01.__str__() == "Nome: Ollyver Ottoboni, Representacao: Servidor"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[OcupanteCargo]
