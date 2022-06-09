import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_01():
    return baker.make(
        'Unidade',
        uuid='f92d2caf-d71f-4ed0-87b2-6d326fb648a7',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='GUAIANASES',
        sigla='G'
    )


@pytest.fixture
def unidade_paulo_camilhier_florencano_dre_1(dre_01):
    return baker.make(
        'Unidade',
        uuid="ae06f0f7-0aca-41d6-94c3-dea20558627d",
        codigo_eol="000086",
        tipo_unidade="EMEI",
        nome="PAULO CAMILHIER FLORENCANO",
        sigla="",
        dre=dre_01,
        email="",
        telefone="",
        tipo_logradouro="",
        logradouro="",
        numero="",
        complemento="",
        bairro="",
        cep="",
        diretor_nome="",
        dre_cnpj="",
        dre_diretor_regional_rf="",
        dre_diretor_regional_nome="",
        dre_designacao_portaria="",
        dre_designacao_ano=""
    )


def test_api_list_unidades_todas(
    jwt_authenticated_client_a,
    unidade_paulo_camilhier_florencano_dre_1,
    dre_01,
    dre,
    unidade
):
    response = jwt_authenticated_client_a.get(f'/api/unidades/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'bairro': '',
            'cep': '',
            'codigo_eol': '99999',
            'complemento': '',
            'diretor_nome': '',
            'dre': None,
            'dre_cnpj': '',
            'dre_designacao_ano': '',
            'dre_designacao_portaria': '',
            'dre_diretor_regional_nome': '',
            'dre_diretor_regional_rf': '',
            'email': '',
            'logradouro': '',
            'nome': 'DRE teste',
            'numero': '',
            'qtd_alunos': 0,
            'sigla': 'TT',
            'telefone': '',
            'tipo_logradouro': '',
            'tipo_unidade': 'DRE',
            'uuid': str(dre.uuid)
        },
        {
            'bairro': 'COHAB INSTITUTO ADVENTISTA',
            'cep': '5868120',
            'codigo_eol': '123456',
            'complemento': 'fundos',
            'diretor_nome': 'Pedro Amaro',
            'dre': {'codigo_eol': '99999',
                    'nome': 'DRE teste',
                    'sigla': 'TT',
                    'tipo_unidade': 'DRE',
                    'uuid': str(dre.uuid)},
            'dre_cnpj': '63.058.286/0001-86',
            'dre_designacao_ano': '2017',
            'dre_designacao_portaria': 'Portaria nº 0.000',
            'dre_diretor_regional_nome': 'Anthony Edward Stark',
            'dre_diretor_regional_rf': '1234567',
            'email': 'emefjopfilho@sme.prefeitura.sp.gov.br',
            'logradouro': 'dos Testes',
            'nome': 'Escola Teste',
            'numero': '200',
            'qtd_alunos': 0,
            'sigla': 'ET',
            'telefone': '58212627',
            'tipo_logradouro': 'Travessa',
            'tipo_unidade': 'CEU',
            'uuid': str(unidade.uuid)
        },
        {
            "uuid": f'{dre_01.uuid}',
            "codigo_eol": f'{dre_01.codigo_eol}',
            "tipo_unidade": f'{dre_01.tipo_unidade}',
            "nome": f'{dre_01.nome}',
            "sigla": f'{dre_01.sigla}',
            "dre": None,
            "email": f'{dre_01.email}',
            "telefone": f'{dre_01.telefone}',
            "tipo_logradouro": f'{dre_01.tipo_logradouro}',
            "logradouro": f'{dre_01.logradouro}',
            "numero": f'{dre_01.numero}',
            "complemento": f'{dre_01.complemento}',
            "bairro": f'{dre_01.bairro}',
            "cep": f'{dre_01.cep}',
            "qtd_alunos": 0,
            "diretor_nome": f'{dre_01.diretor_nome}',
            "dre_cnpj": f'{dre_01.dre_cnpj}',
            "dre_diretor_regional_rf": f'{dre_01.dre_diretor_regional_rf}',
            "dre_diretor_regional_nome": f'{dre_01.dre_diretor_regional_nome}',
            "dre_designacao_portaria": f'{dre_01.dre_designacao_portaria}',
            "dre_designacao_ano": f'{dre_01.dre_designacao_ano}',
        },
        {
            "uuid": f'{unidade_paulo_camilhier_florencano_dre_1.uuid}',
            "codigo_eol": f'{unidade_paulo_camilhier_florencano_dre_1.codigo_eol}',
            "tipo_unidade": f'{unidade_paulo_camilhier_florencano_dre_1.tipo_unidade}',
            "nome": f'{unidade_paulo_camilhier_florencano_dre_1.nome}',
            "sigla": f'{unidade_paulo_camilhier_florencano_dre_1.sigla}',
            "dre": {
                'uuid': f'{unidade_paulo_camilhier_florencano_dre_1.dre.uuid}',
                'codigo_eol': f'{unidade_paulo_camilhier_florencano_dre_1.dre.codigo_eol}',
                'tipo_unidade': f'{unidade_paulo_camilhier_florencano_dre_1.dre.tipo_unidade}',
                'nome': f'{unidade_paulo_camilhier_florencano_dre_1.dre.nome}',
                'sigla': f'{unidade_paulo_camilhier_florencano_dre_1.dre.sigla}',
            },
            "email": f'{unidade_paulo_camilhier_florencano_dre_1.email}',
            "telefone": f'{unidade_paulo_camilhier_florencano_dre_1.telefone}',
            "tipo_logradouro": f'{unidade_paulo_camilhier_florencano_dre_1.tipo_logradouro}',
            "logradouro": f'{unidade_paulo_camilhier_florencano_dre_1.logradouro}',
            "numero": f'{unidade_paulo_camilhier_florencano_dre_1.numero}',
            "complemento": f'{unidade_paulo_camilhier_florencano_dre_1.complemento}',
            "bairro": f'{unidade_paulo_camilhier_florencano_dre_1.bairro}',
            "cep": f'{unidade_paulo_camilhier_florencano_dre_1.cep}',
            "qtd_alunos": 0,
            "diretor_nome": f'{unidade_paulo_camilhier_florencano_dre_1.diretor_nome}',
            "dre_cnpj": f'{unidade_paulo_camilhier_florencano_dre_1.dre_cnpj}',
            "dre_diretor_regional_rf": f'{unidade_paulo_camilhier_florencano_dre_1.dre_diretor_regional_rf}',
            "dre_diretor_regional_nome": f'{unidade_paulo_camilhier_florencano_dre_1.dre_diretor_regional_nome}',
            "dre_designacao_portaria": f'{unidade_paulo_camilhier_florencano_dre_1.dre_designacao_portaria}',
            "dre_designacao_ano": f'{unidade_paulo_camilhier_florencano_dre_1.dre_designacao_ano}',
        }

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_unidades_por_nome(
    jwt_authenticated_client_a,
    unidade_paulo_camilhier_florencano_dre_1,
    dre_01,
    dre,
    unidade
):
    response = jwt_authenticated_client_a.get(f'/api/unidades/?search=Escola', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'bairro': 'COHAB INSTITUTO ADVENTISTA',
            'cep': '5868120',
            'codigo_eol': '123456',
            'complemento': 'fundos',
            'diretor_nome': 'Pedro Amaro',
            'dre': {'codigo_eol': '99999',
                    'nome': 'DRE teste',
                    'sigla': 'TT',
                    'tipo_unidade': 'DRE',
                    'uuid': str(dre.uuid)},
            'dre_cnpj': '63.058.286/0001-86',
            'dre_designacao_ano': '2017',
            'dre_designacao_portaria': 'Portaria nº 0.000',
            'dre_diretor_regional_nome': 'Anthony Edward Stark',
            'dre_diretor_regional_rf': '1234567',
            'email': 'emefjopfilho@sme.prefeitura.sp.gov.br',
            'logradouro': 'dos Testes',
            'nome': 'Escola Teste',
            'numero': '200',
            'qtd_alunos': 0,
            'sigla': 'ET',
            'telefone': '58212627',
            'tipo_logradouro': 'Travessa',
            'tipo_unidade': 'CEU',
            'uuid': str(unidade.uuid)
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_unidades_por_codigo_eol(
    jwt_authenticated_client_a,
    unidade_paulo_camilhier_florencano_dre_1,
    dre_01,
    dre,
    unidade
):
    response = jwt_authenticated_client_a.get(f'/api/unidades/?search=123456', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'bairro': 'COHAB INSTITUTO ADVENTISTA',
            'cep': '5868120',
            'codigo_eol': '123456',
            'complemento': 'fundos',
            'diretor_nome': 'Pedro Amaro',
            'dre': {'codigo_eol': '99999',
                    'nome': 'DRE teste',
                    'sigla': 'TT',
                    'tipo_unidade': 'DRE',
                    'uuid': str(dre.uuid)},
            'dre_cnpj': '63.058.286/0001-86',
            'dre_designacao_ano': '2017',
            'dre_designacao_portaria': 'Portaria nº 0.000',
            'dre_diretor_regional_nome': 'Anthony Edward Stark',
            'dre_diretor_regional_rf': '1234567',
            'email': 'emefjopfilho@sme.prefeitura.sp.gov.br',
            'logradouro': 'dos Testes',
            'nome': 'Escola Teste',
            'numero': '200',
            'qtd_alunos': 0,
            'sigla': 'ET',
            'telefone': '58212627',
            'tipo_logradouro': 'Travessa',
            'tipo_unidade': 'CEU',
            'uuid': str(unidade.uuid)
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_unidades_filtro_por_tipo(
    jwt_authenticated_client_a,
    unidade_paulo_camilhier_florencano_dre_1,
    dre_01,
    dre,
    unidade
):
    response = jwt_authenticated_client_a.get(f'/api/unidades/?tipo_unidade=DRE', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'bairro': '',
            'cep': '',
            'codigo_eol': '99999',
            'complemento': '',
            'diretor_nome': '',
            'dre': None,
            'dre_cnpj': '',
            'dre_designacao_ano': '',
            'dre_designacao_portaria': '',
            'dre_diretor_regional_nome': '',
            'dre_diretor_regional_rf': '',
            'email': '',
            'logradouro': '',
            'nome': 'DRE teste',
            'numero': '',
            'qtd_alunos': 0,
            'sigla': 'TT',
            'telefone': '',
            'tipo_logradouro': '',
            'tipo_unidade': 'DRE',
            'uuid': str(dre.uuid)
        },
        {
            "uuid": f'{dre_01.uuid}',
            "codigo_eol": f'{dre_01.codigo_eol}',
            "tipo_unidade": f'{dre_01.tipo_unidade}',
            "nome": f'{dre_01.nome}',
            "sigla": f'{dre_01.sigla}',
            "dre": None,
            "email": f'{dre_01.email}',
            "telefone": f'{dre_01.telefone}',
            "tipo_logradouro": f'{dre_01.tipo_logradouro}',
            "logradouro": f'{dre_01.logradouro}',
            "numero": f'{dre_01.numero}',
            "complemento": f'{dre_01.complemento}',
            "bairro": f'{dre_01.bairro}',
            "cep": f'{dre_01.cep}',
            "qtd_alunos": 0,
            "diretor_nome": f'{dre_01.diretor_nome}',
            "dre_cnpj": f'{dre_01.dre_cnpj}',
            "dre_diretor_regional_rf": f'{dre_01.dre_diretor_regional_rf}',
            "dre_diretor_regional_nome": f'{dre_01.dre_diretor_regional_nome}',
            "dre_designacao_portaria": f'{dre_01.dre_designacao_portaria}',
            "dre_designacao_ano": f'{dre_01.dre_designacao_ano}',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_unidades_por_dre(
    jwt_authenticated_client_a,
    unidade_paulo_camilhier_florencano_dre_1,
    dre_01,
    dre,
    unidade
):
    response = jwt_authenticated_client_a.get(f'/api/unidades/?dre__uuid={dre.uuid}', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'bairro': 'COHAB INSTITUTO ADVENTISTA',
            'cep': '5868120',
            'codigo_eol': '123456',
            'complemento': 'fundos',
            'diretor_nome': 'Pedro Amaro',
            'dre': {'codigo_eol': '99999',
                    'nome': 'DRE teste',
                    'sigla': 'TT',
                    'tipo_unidade': 'DRE',
                    'uuid': str(dre.uuid)},
            'dre_cnpj': '63.058.286/0001-86',
            'dre_designacao_ano': '2017',
            'dre_designacao_portaria': 'Portaria nº 0.000',
            'dre_diretor_regional_nome': 'Anthony Edward Stark',
            'dre_diretor_regional_rf': '1234567',
            'email': 'emefjopfilho@sme.prefeitura.sp.gov.br',
            'logradouro': 'dos Testes',
            'nome': 'Escola Teste',
            'numero': '200',
            'qtd_alunos': 0,
            'sigla': 'ET',
            'telefone': '58212627',
            'tipo_logradouro': 'Travessa',
            'tipo_unidade': 'CEU',
            'uuid': str(unidade.uuid)
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
