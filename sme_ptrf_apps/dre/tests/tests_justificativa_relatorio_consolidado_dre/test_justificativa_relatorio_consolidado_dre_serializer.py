import pytest

from ...api.serializers.justificativa_relatorio_consolidado_dre_serializer import JustificativaRelatorioConsolidadoDreRetrieveSerializer

pytestmark = pytest.mark.django_db

def test_justificativa_relatorio_consolidado_dre_retrieve_serializer(justificativa_relatorio_dre_consolidado):
    serializer = JustificativaRelatorioConsolidadoDreRetrieveSerializer(justificativa_relatorio_dre_consolidado)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['dre']
    assert serializer.data['periodo']
    assert serializer.data['tipo_conta']
    assert serializer.data['texto']
