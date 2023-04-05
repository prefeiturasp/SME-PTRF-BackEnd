import pytest

from ...api.serializers import FalhaGeracaoPcSerializer

pytestmark = pytest.mark.django_db


def test_falha_geracao_pc_serializer(falha_geracao_pc_teste_falha_geracao_pc_01):
    serializer = FalhaGeracaoPcSerializer(falha_geracao_pc_teste_falha_geracao_pc_01)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['ultimo_usuario']
    assert serializer.data['associacao']
    assert serializer.data['periodo']
    assert serializer.data['data_hora_ultima_ocorrencia']
    assert serializer.data['qtd_ocorrencias_sucessivas']
    assert serializer.data['resolvido']
