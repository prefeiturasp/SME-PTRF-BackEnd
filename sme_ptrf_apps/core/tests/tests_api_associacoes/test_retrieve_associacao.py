import json

import pytest
from model_bakery import baker
from rest_framework import status

from ....core.choices import MembroEnum, RepresentacaoCargo

pytestmark = pytest.mark.django_db

@pytest.fixture
def presidente_associacao(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567432',
        email='arthur@gmail.com'
    )

@pytest.fixture
def presidente_conselho_fiscal(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='José Firmino',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567433',
        email='jose@gmail.com'
    )



def test_api_retrieve_associacao(client, associacao, presidente_associacao, presidente_conselho_fiscal):
    response = client.get(f'/api/associacoes/{associacao.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{associacao.uuid}',
        'ccm': f'{associacao.ccm}',
        'cnpj': f'{associacao.cnpj}',
        'email': f'{associacao.email}',
        'nome': f'{associacao.nome}',
        'status_regularidade': f'{associacao.status_regularidade}',
        'presidente_associacao': {
            'nome': presidente_associacao.nome,
            'email': presidente_associacao.email,
            'cargo_educacao': presidente_associacao.cargo_educacao
        },
        'presidente_conselho_fiscal': {
            'nome': presidente_conselho_fiscal.nome,
            'email': presidente_conselho_fiscal.email,
            'cargo_educacao': presidente_conselho_fiscal.cargo_educacao
        },
        'processo_regularidade': '123456',
        'unidade': {
            'codigo_eol': f'{associacao.unidade.codigo_eol}',
            'dre': {
                'codigo_eol': f'{associacao.unidade.dre.codigo_eol}',
                'nome': f'{associacao.unidade.dre.nome}',
                'sigla': f'{associacao.unidade.dre.sigla}',
                'tipo_unidade': 'DRE',
                'uuid': f'{associacao.unidade.dre.uuid}'
            },
            'nome': f'{associacao.unidade.nome}',
            'sigla': f'{associacao.unidade.sigla}',
            'tipo_unidade': f'{associacao.unidade.tipo_unidade}',
            'uuid': f'{associacao.unidade.uuid}',
            'email': f'{associacao.unidade.email}',
            'qtd_alunos': associacao.unidade.qtd_alunos,
            'tipo_logradouro': f'{associacao.unidade.tipo_logradouro}',
            'logradouro': f'{associacao.unidade.logradouro}',
            'numero': f'{associacao.unidade.numero}',
            'complemento': f'{associacao.unidade.complemento}',
            'bairro': f'{associacao.unidade.bairro}',
            'cep': f'{associacao.unidade.cep}',
            'telefone': f'{associacao.unidade.telefone}',
            'diretor_nome': f'{associacao.unidade.diretor_nome}',
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
