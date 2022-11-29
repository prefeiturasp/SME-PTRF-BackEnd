import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import TipoAcertoDocumento

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_documento_ata():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas')


@pytest.fixture
def tipo_acerto_documento(tipo_documento_ata):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar com assinatura')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_ata)
    tipo_acerto.save()
    return tipo_acerto


def test_instance_model(tipo_acerto_documento):
    model = tipo_acerto_documento
    assert isinstance(model, TipoAcertoDocumento)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.tipos_documento_prestacao
    assert model.categoria
    assert model.ativo


def test_srt_model(tipo_acerto_documento):
    assert str(tipo_acerto_documento) == 'Enviar com assinatura'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoAcertoDocumento]
