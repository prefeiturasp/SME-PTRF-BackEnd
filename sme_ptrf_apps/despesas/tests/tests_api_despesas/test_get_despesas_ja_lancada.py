import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesa_ja_lancada_sim(associacao, jwt_authenticated_client, despesa):
    params = f'tipo_documento={despesa.tipo_documento.id}' \
             f'&numero_documento={despesa.numero_documento}' \
             f'&cpf_cnpj_fornecedor={despesa.cpf_cnpj_fornecedor}' \
             f'&associacao__uuid={associacao.uuid}'

    response = jwt_authenticated_client.get(f'/api/despesas/ja-lancada/?{params}', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'despesa_ja_lancada': True,
        'uuid_despesa': f'{despesa.uuid}'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_despesa_ja_lancada_alteracao(associacao, jwt_authenticated_client, despesa):
    params = f'tipo_documento={despesa.tipo_documento.id}' \
             f'&numero_documento={despesa.numero_documento}' \
             f'&cpf_cnpj_fornecedor={despesa.cpf_cnpj_fornecedor}' \
             f'&associacao__uuid={associacao.uuid}' \
             f'&despesa_uuid={despesa.uuid}'

    response = jwt_authenticated_client.get(f'/api/despesas/ja-lancada/?{params}', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'despesa_ja_lancada': False,
        'uuid_despesa': ''
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_despesa_ja_lancada_nao(associacao, jwt_authenticated_client, tipo_documento, fornecedor_jose):
    params = f'tipo_documento={tipo_documento.id}' \
             f'&numero_documento=123456789' \
             f'&cpf_cnpj_fornecedor={fornecedor_jose.cpf_cnpj}' \
             f'&associacao__uuid={associacao.uuid}'

    response = jwt_authenticated_client.get(f'/api/despesas/ja-lancada/?{params}', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'despesa_ja_lancada': False,
        'uuid_despesa': ''
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_despesa_ja_lancada_nao_outra_associacao(associacao, jwt_authenticated_client, despesa,
                                                         outra_associacao):
    params = f'tipo_documento={despesa.tipo_documento.id}' \
             f'&numero_documento={despesa.numero_documento}' \
             f'&cpf_cnpj_fornecedor={despesa.cpf_cnpj_fornecedor}' \
             f'&associacao__uuid={outra_associacao.uuid}'

    response = jwt_authenticated_client.get(f'/api/despesas/ja-lancada/?{params}', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'despesa_ja_lancada': False,
        'uuid_despesa': ''
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
