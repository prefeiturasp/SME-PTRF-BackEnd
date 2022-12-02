import pytest

from ...api.serializers.comentario_analise_consolidado_dre_serializer import ComentarioAnaliseConsolidadoDRESerializer

pytestmark = pytest.mark.django_db


def test_serializer(comentario_analise_consolidado_dre_01):
    serializer = ComentarioAnaliseConsolidadoDRESerializer(comentario_analise_consolidado_dre_01)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['consolidado_dre']
    assert serializer.data['ordem']
    assert serializer.data['comentario']
    assert serializer.data['notificado'] is False
    assert serializer.data['notificado_em'] is None
