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


def test_audit_log(solicitacao_acerto_documento_ata):
    assert solicitacao_acerto_documento_ata.history.count() == 1  # Um log de inclusão
    assert solicitacao_acerto_documento_ata.history.latest().action == 0  # 0-Inclusão

    solicitacao_acerto_documento_ata.detalhamento = "TESTE"
    solicitacao_acerto_documento_ata.save()
    assert solicitacao_acerto_documento_ata.history.count() == 2  # Um log de inclusão e outro de edição
    assert solicitacao_acerto_documento_ata.history.latest().action == 1  # 1-Edição
