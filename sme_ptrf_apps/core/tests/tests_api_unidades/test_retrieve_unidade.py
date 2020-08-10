import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_unidade_educacional():
    return baker.make(
        'Unidade',
        uuid='f92d2caf-d71f-4ed0-87b2-6d326fb648a7',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='GUAIANASES',
        sigla='G'
    )


@pytest.fixture
def unidade_educacional(dre_unidade_educacional):
    return baker.make(
        'Unidade',
        uuid="c5ae0767-9626-4801-9ed9-56808858b6d8",
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre_unidade_educacional,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        qtd_alunos=0,
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


def test_api_retrieve_unidade(client, unidade_educacional):
    response = client.get(f'/api/unidades/{unidade_educacional.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = {
        "uuid": f'{unidade_educacional.uuid}',
        "codigo_eol": f'{unidade_educacional.codigo_eol}',
        "tipo_unidade": f'{unidade_educacional.tipo_unidade}',
        "nome": f'{unidade_educacional.nome}',
        "sigla": f'{unidade_educacional.sigla}',
        "dre": {
            'uuid': f'{unidade_educacional.dre.uuid}',
            'codigo_eol': f'{unidade_educacional.dre.codigo_eol}',
            'tipo_unidade': f'{unidade_educacional.dre.tipo_unidade}',
            'nome': f'{unidade_educacional.dre.nome}',
            'sigla': f'{unidade_educacional.dre.sigla}',
        },
        "email": f'{unidade_educacional.email}',
        "telefone": f'{unidade_educacional.telefone}',
        "tipo_logradouro": f'{unidade_educacional.tipo_logradouro}',
        "logradouro": f'{unidade_educacional.logradouro}',
        "numero": f'{unidade_educacional.numero}',
        "complemento": f'{unidade_educacional.complemento}',
        "bairro": f'{unidade_educacional.bairro}',
        "cep": f'{unidade_educacional.cep}',
        "qtd_alunos": 0,
        "diretor_nome": f'{unidade_educacional.diretor_nome}',
        "dre_cnpj": f'{unidade_educacional.dre_cnpj}',
        "dre_diretor_regional_rf": f'{unidade_educacional.dre_diretor_regional_rf}',
        "dre_diretor_regional_nome": f'{unidade_educacional.dre_diretor_regional_nome}',
        "dre_designacao_portaria": f'{unidade_educacional.dre_designacao_portaria}',
        "dre_designacao_ano": f'{unidade_educacional.dre_designacao_ano}',
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
