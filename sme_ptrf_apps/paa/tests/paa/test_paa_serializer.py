import pytest

from sme_ptrf_apps.paa.api.serializers import PaaSerializer

pytestmark = pytest.mark.django_db


def test_paa_retriever_serializer(paa):
    serializer = PaaSerializer(paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'periodo_paa' in serializer.data
    assert 'associacao' in serializer.data
    assert 'periodo_paa_objeto' in serializer.data
    assert 'saldo_congelado_em' in serializer.data
