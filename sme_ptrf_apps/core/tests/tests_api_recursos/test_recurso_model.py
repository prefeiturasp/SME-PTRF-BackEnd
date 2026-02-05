import pytest
from django.contrib import admin

from ...models import Recurso

pytestmark = pytest.mark.django_db


def test_instance_model(recurso):
    model = recurso
    assert isinstance(model, Recurso)
    assert model.nome
    assert model.nome_exibicao
    assert model.ativo
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.cor
    assert not model.legado
    assert not model.logo
    assert not model.icone


def test_srt_model(recurso):
    assert recurso.__str__() == 'Recurso 3'


def test_admin():
    assert admin.site._registry[Recurso]


def test_criar_recurso_basico(recurso_factory):
    """Teste criação básica de recurso com todos os campos"""
    recurso = recurso_factory.create(
        nome='PTRF',
        nome_exibicao='Programa PTRF',
        cor=Recurso.CorChoices.AZUL,
        ativo=True,
        legado=False
    )

    assert recurso.pk is not None
    assert recurso.nome == 'PTRF'
    assert recurso.nome_exibicao == 'Programa PTRF'
    assert recurso.cor == Recurso.CorChoices.AZUL
    assert recurso.ativo is True
    assert recurso.legado is False


def test_str_retorna_nome(recurso):
    """Teste __str__ retorna nome do recurso"""
    assert str(recurso) == recurso.nome


def test_recurso_ativo_por_padrao(recurso_factory):
    """Teste que recurso é criado ativo por padrão"""
    recurso = recurso_factory.create()
    assert recurso.ativo is True


def test_recurso_tem_campos_opcionais(recurso_factory):
    """Teste que logo e icone são opcionais"""
    recurso = recurso_factory.create(logo=None, icone=None)
    assert not recurso.logo
    assert not recurso.icone
