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


def test_api_list_unidades_dres_todas(jwt_authenticated_client_a, unidade_paulo_camilhier_florencano_dre_1, dre_01, dre):
    response = jwt_authenticated_client_a.get(f'/api/dres/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
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
            'observacao': f'{dre_01.observacao}',
            "qtd_alunos": 0,
            "diretor_nome": f'{dre_01.diretor_nome}',
            "dre_cnpj": f'{dre_01.dre_cnpj}',
            "dre_diretor_regional_rf": f'{dre_01.dre_diretor_regional_rf}',
            "dre_diretor_regional_nome": f'{dre_01.dre_diretor_regional_nome}',
            "dre_designacao_portaria": f'{dre_01.dre_designacao_portaria}',
            "dre_designacao_ano": f'{dre_01.dre_designacao_ano}',
        },
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
            'observacao': '',
            'qtd_alunos': 0,
            'sigla': 'TT',
            'telefone': '',
            'tipo_logradouro': '',
            'tipo_unidade': 'DRE',
            'uuid': str(dre.uuid)
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
