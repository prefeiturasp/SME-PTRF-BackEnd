import pytest
from model_bakery import baker

from ...api.serializers.tipo_devolucao_ao_tesouro_serializer import (TipoDevolucaoAoTesouroSerializer)

pytestmark = pytest.mark.django_db

@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


def test_serializer(tipo_devolucao_ao_tesouro):

    serializer = TipoDevolucaoAoTesouroSerializer(tipo_devolucao_ao_tesouro)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['uuid']
