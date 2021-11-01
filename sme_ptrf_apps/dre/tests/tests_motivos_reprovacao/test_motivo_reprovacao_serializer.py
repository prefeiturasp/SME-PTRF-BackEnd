import pytest

from ...api.serializers.motivo_reprovacao_serializer import MotivoReprovacaoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(motivo_reprovacao_x):
    serializer = MotivoReprovacaoSerializer(motivo_reprovacao_x)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['motivo']
