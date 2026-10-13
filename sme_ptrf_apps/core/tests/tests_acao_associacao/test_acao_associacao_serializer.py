import pytest

from ...api.serializers.acao_associacao_serializer import (
    AcaoAssociacaoSerializer,
    AcaoAssociacaoLookUpSerializer,
    AcaoAssociacaoCreateSerializer,
    AcaoAssociacaoRetrieveSerializer,
    AcaoAssociacaoConciliacaoLookUpSerializer
)

pytestmark = pytest.mark.django_db


def test_serializer_conciliacao(acao_associacao):
    serializer = AcaoAssociacaoConciliacaoLookUpSerializer(acao_associacao)

    assert serializer.data is not None
    assert 'id' in serializer.data
    assert 'uuid' in serializer.data
    assert 'acao' in serializer.data
    assert 'nome' in serializer.data
    assert 'e_recursos_proprios' in serializer.data


def test_serializer(acao_associacao):
    serializer = AcaoAssociacaoSerializer(acao_associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['acao']
    assert serializer.data['associacao']
    assert serializer.data['status']


def test_lookup_serializer(acao_associacao):
    serializer = AcaoAssociacaoLookUpSerializer(acao_associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['nome']


def test_create_serializer(acao_associacao):
    serializer = AcaoAssociacaoCreateSerializer(acao_associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['acao']
    assert serializer.data['associacao']
    assert serializer.data['status']


def test_retrieave_serializer(acao_associacao):
    serializer = AcaoAssociacaoRetrieveSerializer(acao_associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['acao']
    assert serializer.data['associacao']
    assert serializer.data['status']
    assert serializer.data['criado_em']
