import pytest

from ...api.serializers.unidade_serializer import (UnidadeLookUpSerializer, UnidadeSerializer, UnidadeInfoAtaSerializer,
                                                   UnidadeListEmAssociacoesSerializer)

pytestmark = pytest.mark.django_db


def test_unidade_lookup_serializer(unidade):
    unidade_serializer = UnidadeLookUpSerializer(unidade)

    assert unidade_serializer.data is not None
    assert 'id' not in unidade_serializer.data
    assert 'sigla' in unidade_serializer.data


def test_unidade_serializer(unidade):
    unidade_serializer = UnidadeSerializer(unidade)

    assert unidade_serializer.data is not None
    assert 'id' not in unidade_serializer.data
    assert unidade_serializer.data['dre']
    assert 'sigla' in unidade_serializer.data
    assert 'cep' in unidade_serializer.data
    assert 'tipo_logradouro' in unidade_serializer.data
    assert 'logradouro' in unidade_serializer.data
    assert 'bairro' in unidade_serializer.data
    assert 'numero' in unidade_serializer.data
    assert 'complemento' in unidade_serializer.data
    assert 'telefone' in unidade_serializer.data
    assert 'email' in unidade_serializer.data
    assert 'qtd_alunos' in unidade_serializer.data
    assert 'diretor_nome' in unidade_serializer.data
    assert 'dre_cnpj' in unidade_serializer.data
    assert 'dre_diretor_regional_rf' in unidade_serializer.data
    assert 'dre_diretor_regional_nome' in unidade_serializer.data
    assert 'dre_designacao_portaria' in unidade_serializer.data
    assert 'dre_designacao_ano' in unidade_serializer.data


def test_unidade_info_ata_serializer(unidade):
    unidade_serializer = UnidadeInfoAtaSerializer(unidade)
    assert unidade_serializer.data is not None
    assert 'tipo_unidade' in unidade_serializer.data
    assert 'nome' in unidade_serializer.data


def test_unidade_list_serializer(unidade):
    unidade_serializer = UnidadeListEmAssociacoesSerializer(unidade)
    assert unidade_serializer.data is not None
    assert 'uuid' in unidade_serializer.data
    assert 'codigo_eol' in unidade_serializer.data
    assert 'nome_com_tipo' in unidade_serializer.data
