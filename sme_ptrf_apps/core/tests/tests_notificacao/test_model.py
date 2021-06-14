import pytest


from django.contrib import admin
from model_bakery import baker
from django.contrib.auth import get_user_model
from ...models import Notificacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def notificacao(usuario_permissao_associacao):
    return baker.make(
        'Notificacao',
        tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
        categoria=Notificacao.CATEGORIA_NOTIFICACAO_COMENTARIO_PC,
        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
        titulo="Documentos Faltantes",
        descricao="Documentos Faltantes na prestação de contas",
        usuario=usuario_permissao_associacao
    )


def test_instance_model(notificacao):
    model = notificacao
    assert isinstance(model, Notificacao)
    assert model.titulo
    assert model.descricao
    assert model.tipo
    assert model.categoria
    assert model.remetente
    assert isinstance(model.usuario, get_user_model())
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(notificacao):
    assert str(notificacao) == "Documentos Faltantes"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Notificacao]
