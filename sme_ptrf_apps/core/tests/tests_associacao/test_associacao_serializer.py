import pytest
from rest_framework.exceptions import ValidationError

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


def test_associacao_create_serializer_sem_nome_dre():
    serializer = AssociacaoCreateSerializer(data={
        'nome': 'APM Nova Escola',
        'unidade': {
            'codigo_eol': '789123',
            'nome': 'EMEF Nova Escola',
            'email': 'emefnova@escola.sp.gov.br',
            'telefone': '11912345678',
            'numero': '123',
            'tipo_logradouro': 'Rua',
            'logradouro': 'Nova',
            'bairro': 'Centro',
            'cep': '01001000',
            'tipo_unidade': 'EMEF',
            'observacao': 'Unidade gerada para teste',
        }
    })

    assert serializer.is_valid(), serializer.errors

    with pytest.raises(ValidationError) as erro:
        serializer.save()

    assert erro.value.detail == {'nome_dre': ['EOL informado não possui DRE.']}
