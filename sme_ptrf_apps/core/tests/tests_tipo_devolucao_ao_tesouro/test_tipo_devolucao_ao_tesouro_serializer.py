import pytest
from model_bakery import baker
from rest_framework.exceptions import ValidationError
from ...api.serializers.tipo_devolucao_ao_tesouro_serializer import (TipoDevolucaoAoTesouroSerializer)
from ...models import TipoDevolucaoAoTesouro

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


def test_create_tipo_devolucao_ao_tesouro_success():
    """
    Testa a criação de um TipoDevolucaoAoTesouro com dados válidos.
    """
    data = {
        "nome": "Devolução ao Tesouro Teste",
    }

    serializer = TipoDevolucaoAoTesouroSerializer(data=data)
    assert serializer.is_valid(), f"Erros: {serializer.errors}"

    tipo_devolucao_ao_tesouro = serializer.save()
    assert tipo_devolucao_ao_tesouro.nome == data["nome"]
    assert TipoDevolucaoAoTesouro.objects.count() == 1


def test_update_tipo_devolucao_ao_tesouro_success(tipo_devolucao_ao_tesouro):
    """
    Testa a atualização de um TipoDevolucaoAoTesouro com um nome novo.
    """
    data = {
        "nome": "Devolução ao Tesouro Atualizado",
    }

    serializer = TipoDevolucaoAoTesouroSerializer(instance=tipo_devolucao_ao_tesouro, data=data, partial=True)
    assert serializer.is_valid(), f"Erros: {serializer.errors}"

    tipo_devolucao_ao_tesouro_atualizado = serializer.save()
    assert tipo_devolucao_ao_tesouro_atualizado.nome == "Devolução ao Tesouro Atualizado"
