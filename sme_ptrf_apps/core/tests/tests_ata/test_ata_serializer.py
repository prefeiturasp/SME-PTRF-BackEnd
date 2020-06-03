import pytest

from ...api.serializers import AtaLookUpSerializer

pytestmark = pytest.mark.django_db


def test_lookup_serializer(ata_prestacao_conta_iniciada):

    serializer = AtaLookUpSerializer(ata_prestacao_conta_iniciada)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['alterado_em']
