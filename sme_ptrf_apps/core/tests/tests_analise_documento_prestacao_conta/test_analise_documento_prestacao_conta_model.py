import pytest
from django.contrib import admin

from ...models import AnalisePrestacaoConta, TipoDocumentoPrestacaoConta, AnaliseDocumentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_instance_model(analise_documento_prestacao_conta_2020_1_ata_correta):
    model = analise_documento_prestacao_conta_2020_1_ata_correta
    assert isinstance(model, AnaliseDocumentoPrestacaoConta)
    assert isinstance(model.analise_prestacao_conta, AnalisePrestacaoConta)
    assert isinstance(model.tipo_documento_prestacao_conta, TipoDocumentoPrestacaoConta)
    assert model.resultado == AnaliseDocumentoPrestacaoConta.RESULTADO_CORRETO


def test_srt_model(analise_documento_prestacao_conta_2020_1_ata_correta):
    esperado = f'Análise de documento {analise_documento_prestacao_conta_2020_1_ata_correta.uuid} - Resultado:CORRETO'
    assert analise_documento_prestacao_conta_2020_1_ata_correta.__str__() == esperado


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseDocumentoPrestacaoConta]
