import pytest
from django.contrib import admin

from ...models import (
    AnaliseDocumentoPrestacaoConta,
    SolicitacaoAcertoDocumento,
    TipoAcertoDocumento,
)

pytestmark = pytest.mark.django_db


def test_instance_model(solicitacao_acerto_documento_ata):
    model = solicitacao_acerto_documento_ata
    assert isinstance(model, SolicitacaoAcertoDocumento)
    assert isinstance(model.analise_documento, AnaliseDocumentoPrestacaoConta)
    assert isinstance(model.tipo_acerto, TipoAcertoDocumento)
    assert model.detalhamento


def test_srt_model(solicitacao_acerto_documento_ata):
    assert solicitacao_acerto_documento_ata.__str__() == 'Enviar com assinatura - Detalhamento motivo acerto no documento'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[SolicitacaoAcertoDocumento]
