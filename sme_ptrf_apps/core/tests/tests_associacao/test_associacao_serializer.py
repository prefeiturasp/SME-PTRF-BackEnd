import pytest

from ...api.serializers.associacao_serializer import (AssociacaoSerializer, AssociacaoLookupSerializer,
                                                      AssociacaoCreateSerializer, AssociacaoListSerializer,
                                                      AssociacaoCompletoSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(associacao):
    serializer = AssociacaoSerializer(associacao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['unidade']
    assert serializer.data['cnpj']
    assert serializer.data['ccm']
    assert serializer.data['processo_regularidade']


def test_lookup_serializer(associacao):
    serializer = AssociacaoLookupSerializer(associacao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']


def test_create_serializer(associacao):
    serializer = AssociacaoCreateSerializer(associacao)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['unidade']
    assert serializer.data['cnpj']
    assert serializer.data['processo_regularidade']


def test_list_serializer(associacao):
    serializer = AssociacaoListSerializer(associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['unidade']
    assert serializer.data['status_regularidade']


def test_completo_serializer(associacao, membro_associacao_presidente_associacao, membro_associacao_presidente_conselho):
    serializer = AssociacaoCompletoSerializer(associacao)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['unidade']
    assert serializer.data['cnpj']
    assert serializer.data['ccm']
    assert serializer.data['presidente_associacao']
    assert serializer.data['presidente_conselho_fiscal']
    assert serializer.data['processo_regularidade']
