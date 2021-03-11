import pytest
from sme_ptrf_apps.core.api.serializers import AmbienteSerializer

pytestmark = pytest.mark.django_db


def test_ambiente_serializer(ambiente_dev):
    serializer = AmbienteSerializer(ambiente_dev)
    campos_esperados = [
        'id',
        'prefixo',
        'nome'
    ]

    assert serializer.data
    assert [key for key in serializer.data.keys()] == campos_esperados
