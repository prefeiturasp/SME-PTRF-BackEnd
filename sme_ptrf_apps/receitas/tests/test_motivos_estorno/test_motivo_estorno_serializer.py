import pytest
from sme_ptrf_apps.receitas.api.serializers.motivo_estorno_serializer import MotivoEstornoSerializer

pytestmark = pytest.mark.django_db


def test_serializer(motivo_estorno_01):
    serializer = MotivoEstornoSerializer(motivo_estorno_01)

    assert serializer.data['id']
    assert serializer.data['motivo']
