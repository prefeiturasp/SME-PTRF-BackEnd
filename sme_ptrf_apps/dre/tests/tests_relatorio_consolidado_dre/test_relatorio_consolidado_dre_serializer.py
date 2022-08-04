import pytest

from ...api.serializers.relatorio_consolidado_dre_serializer import RelatorioConsolidadoDreSerializer

pytestmark = pytest.mark.django_db


def test_serializer(relatorio_dre_consolidado_gerado_total):
    serializer = RelatorioConsolidadoDreSerializer(relatorio_dre_consolidado_gerado_total)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['arquivo']
    assert serializer.data['versao']
    assert serializer.data['tipo_conta']
