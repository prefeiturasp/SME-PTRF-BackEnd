import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import TipoDocumentoPrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_documento_prestacao_conta():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas', documento_por_conta=True)


def test_instance_model(tipo_documento_prestacao_conta):
    model = tipo_documento_prestacao_conta
    assert isinstance(model, TipoDocumentoPrestacaoConta)
    assert model.nome
    assert model.documento_por_conta
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(tipo_documento_prestacao_conta):
    assert str(tipo_documento_prestacao_conta) == 'Cópia da ata da prestação de contas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoDocumentoPrestacaoConta]
