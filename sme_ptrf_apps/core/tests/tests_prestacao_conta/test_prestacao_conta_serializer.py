import pytest

from ...api.serializers.prestacao_conta_serializer import PrestacaoContaLookUpSerializer

pytestmark = pytest.mark.django_db


def test_lookup_serializer(prestacao_conta):
    serializer = PrestacaoContaLookUpSerializer(prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['periodo_uuid']
    assert serializer.data['conta_associacao_uuid']
    assert serializer.data['status']
    assert serializer.data['conciliado']
    assert serializer.data['conciliado_em']
    assert serializer.data['observacoes']
    assert serializer.data['motivo_reabertura']
