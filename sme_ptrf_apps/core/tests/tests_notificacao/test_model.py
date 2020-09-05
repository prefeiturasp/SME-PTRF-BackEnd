import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import Categoria, Notificacao, Remetente, TipoNotificacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def categoria():
    return baker.make('Categoria', nome='Prestações de conta')

@pytest.fixture
def tipo_notificacao():
    return baker.make('TipoNotificacao', nome='Informação')

@pytest.fixture
def remetente():
    return baker.make('Remetente', nome='SME')

@pytest.fixture
def notificacao(tipo_notificacao, remetente, categoria):
    return baker.make(
        'Notificacao',
        tipo=tipo_notificacao,
        categoria=categoria,
        remetente=remetente,
        titulo="Documentos Faltantes",
        descricao="Documentos Faltantes na prestação de contas"
    )

def test_instance_model(notificacao):
    model = notificacao
    assert isinstance(model, Notificacao)
    assert model.titulo
    assert model.descricao
    assert isinstance(model.remetente, Remetente)
    assert isinstance(model.tipo, TipoNotificacao)
    assert isinstance(model.categoria, Categoria)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(notificacao):
    assert str(notificacao) == "Documentos Faltantes"


def test_meta_modelo(notificacao):
    assert notificacao._meta.verbose_name == 'Notificação'
    assert notificacao._meta.verbose_name_plural == 'Notificações'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Notificacao]
