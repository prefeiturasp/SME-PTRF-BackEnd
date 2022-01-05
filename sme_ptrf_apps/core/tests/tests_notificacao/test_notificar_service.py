import pytest

from model_bakery import baker
from freezegun import freeze_time

from ...models import Notificacao, NotificacaoCreateException

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


def test_notificar_cria_notificacao(usuario_permissao_associacao):
    assert not Notificacao.objects.exists()

    Notificacao.notificar(
        tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
        remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
        titulo="Teste",
        descricao="Esse é um teste.",
        usuario=usuario_permissao_associacao
    )

    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_DRE
    assert notificacao.titulo == "Teste"
    assert notificacao.descricao == "Esse é um teste."
    assert notificacao.usuario == usuario_permissao_associacao


def test_notificar_nao_permite_tipo_invalido(usuario_permissao_associacao):

    with pytest.raises(NotificacaoCreateException):
        Notificacao.notificar(
            tipo='INVALIDO',
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
            titulo="Teste",
            descricao="Esse é um teste.",
            usuario=usuario_permissao_associacao
        )


def test_notificar_nao_permite_categoria_invalida(usuario_permissao_associacao):

    with pytest.raises(NotificacaoCreateException):
        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
            categoria='INVALIDO',
            remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
            titulo="Teste",
            descricao="Esse é um teste.",
            usuario=usuario_permissao_associacao
        )


def test_notificar_nao_permite_remetente_invalido(usuario_permissao_associacao):

    with pytest.raises(NotificacaoCreateException):
        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
            remetente='INVALIDO',
            titulo="Teste",
            descricao="Esse é um teste.",
            usuario=usuario_permissao_associacao
        )


def test_notificar_nao_permite_titulo_vazio(usuario_permissao_associacao):

    with pytest.raises(NotificacaoCreateException):
        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
            titulo="",
            descricao="Esse é um teste.",
            usuario=usuario_permissao_associacao
        )


def test_notificar_nao_permite_usuario_vazio(usuario_permissao_associacao):

    with pytest.raises(NotificacaoCreateException):
        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
            titulo="Teste",
            descricao="Esse é um teste.",
            usuario=None
        )


def test_notificar_re_notificar_false(notificacao, usuario_permissao_associacao):

    assert Notificacao.objects.count() == 1

    Notificacao.notificar(
        tipo=notificacao.tipo,
        categoria=notificacao.categoria,
        remetente=notificacao.remetente,
        titulo=notificacao.titulo,
        descricao=notificacao.descricao,
        usuario=notificacao.usuario,
        renotificar=False,
    )

    assert Notificacao.objects.count() == 1


@freeze_time("2021-01-01 10:20:30")
def test_notificar_re_notificar_true(notificacao, usuario_permissao_associacao):

    assert Notificacao.objects.count() == 1

    Notificacao.notificar(
        tipo=notificacao.tipo,
        categoria=notificacao.categoria,
        remetente=notificacao.remetente,
        titulo=notificacao.titulo,
        descricao=notificacao.descricao,
        usuario=notificacao.usuario,
        renotificar=True,
    )

    assert Notificacao.objects.count() == 2


def test_notificar_re_notificar_true_nao_repetido(usuario_permissao_associacao):

    assert Notificacao.objects.count() == 0

    Notificacao.notificar(
        tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
        remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
        titulo="Teste",
        descricao="Esse é um teste",
        usuario=usuario_permissao_associacao,
        renotificar=True,
    )

    assert Notificacao.objects.count() == 1

