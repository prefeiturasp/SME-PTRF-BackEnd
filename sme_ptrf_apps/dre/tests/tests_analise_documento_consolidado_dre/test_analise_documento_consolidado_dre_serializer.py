import pytest

from ...api.serializers.analise_documento_consolidado_dre_serializer import AnalisesDocumentosConsolidadoDreSerializer

pytestmark = pytest.mark.django_db


def test_serializer(analise_documento_consolidado_dre_01):
    serializer = AnalisesDocumentosConsolidadoDreSerializer(analise_documento_consolidado_dre_01)

    assert serializer.data is not None
    assert serializer.data['analise_consolidado_dre']
    assert serializer.data['documento_adicional']
    assert serializer.data['relatorio_consolidao_dre']
    assert serializer.data['ata_parecer_tecnico']
    assert serializer.data['detalhamento'] is ""
    assert serializer.data['resultado']

