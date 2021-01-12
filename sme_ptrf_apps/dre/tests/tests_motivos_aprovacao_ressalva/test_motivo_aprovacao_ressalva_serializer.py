import pytest

from ...api.serializers.motivo_aprovacao_ressalva_serializer import MotivoAprovacaoRessalvaSerializer

pytestmark = pytest.mark.django_db


def test_serializer(motivo_aprovacao_ressalva_x):
    serializer = MotivoAprovacaoRessalvaSerializer(motivo_aprovacao_ressalva_x)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['motivo']
