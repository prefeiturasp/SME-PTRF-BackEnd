import pytest
from model_bakery import baker

from ...api.serializers.unidade_serializer import (
    UnidadeLookUpSerializer,
    UnidadeSerializer,
    UnidadeInfoAtaSerializer,
    UnidadeListEmAssociacoesSerializer,
    UnidadeCreateSerializer,
)

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


def test_unidade_create_serializer_vincula_dre_por_nome():
    dre = baker.make('Unidade', codigo_eol='987654', tipo_unidade='DRE', nome='DRE LESTE')

    serializer = UnidadeCreateSerializer(data={
        'codigo_eol': '654321',
        'nome': 'EMEF Nova Unidade',
        'email': 'contato@escola.sp.gov.br',
        'telefone': '11999999999',
        'numero': '100',
        'tipo_logradouro': 'Rua',
        'logradouro': 'Das Flores',
        'bairro': 'Centro',
        'cep': '01001000',
        'tipo_unidade': 'CEU',
        'observacao': 'Nova unidade de teste',
        'nome_dre': 'dre leste',
    })

    assert serializer.is_valid(), serializer.errors

    unidade = serializer.save()

    assert unidade.dre == dre


def test_unidade_create_serializer_vincula_dre_por_busca_parcial():
    dre = baker.make('Unidade', codigo_eol='111222', tipo_unidade='DRE', nome='DRE NORTE')

    serializer = UnidadeCreateSerializer(data={
        'codigo_eol': '222333',
        'nome': 'EMEI Jardim Vida',
        'email': 'emei@escola.sp.gov.br',
        'telefone': '1188888888',
        'numero': '50',
        'tipo_logradouro': 'Alameda',
        'logradouro': 'Dos Sonhos',
        'bairro': 'Verde',
        'cep': '02020000',
        'tipo_unidade': 'CEI',
        'observacao': 'Unidade com DRE localizada por contains',
        'nome_dre': 'norte',
    })

    assert serializer.is_valid(), serializer.errors

    unidade = serializer.save()

    assert unidade.dre == dre


def test_unidade_create_serializer_sem_dre_encontrada():
    serializer = UnidadeCreateSerializer(data={
        'codigo_eol': '333444',
        'nome': 'EMEF Sem DRE',
        'email': 'emeff@email.com',
        'telefone': '1177777777',
        'numero': '10',
        'tipo_logradouro': 'Avenida',
        'logradouro': 'Central',
        'bairro': 'Centro',
        'cep': '03030000',
        'tipo_unidade': 'CEI',
        'observacao': 'Criação sem DRE associada',
        'nome_dre': 'DRE INEXISTENTE',
    })

    assert serializer.is_valid(), serializer.errors

    unidade = serializer.save()

    assert unidade.dre is None
