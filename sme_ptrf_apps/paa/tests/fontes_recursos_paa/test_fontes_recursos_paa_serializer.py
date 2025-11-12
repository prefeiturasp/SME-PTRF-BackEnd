import pytest

from sme_ptrf_apps.paa.api.serializers.fonte_recurso_paa_serializer import FonteRecursoPaaSerializer

pytestmark = pytest.mark.django_db


def test_fonte_recurso_paa_list_serializer(fonte_recurso_paa):
    serializer = FonteRecursoPaaSerializer(fonte_recurso_paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data
    assert 'id' in serializer.data
