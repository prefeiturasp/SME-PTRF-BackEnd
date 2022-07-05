import pytest

from ...api.serializers.consolidado_dre_serializer import ConsolidadoDreSerializer

pytestmark = pytest.mark.django_db


def test_serializer(consolidado_dre_teste_model_consolidado_dre):
    serializer = ConsolidadoDreSerializer(consolidado_dre_teste_model_consolidado_dre)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['dre']
    assert serializer.data['periodo']
    assert serializer.data['status']
    assert serializer.data['versao']
