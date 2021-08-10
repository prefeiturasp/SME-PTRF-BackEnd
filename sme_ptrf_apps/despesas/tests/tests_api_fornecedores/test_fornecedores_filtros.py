import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_fornecedor_filtro_qualquer_parte_cpf(jwt_authenticated_client, fornecedor_jose):
    response = jwt_authenticated_client.get(f'/api/fornecedores/?cpf_cnpj=079', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "id": fornecedor_jose.id,
            "criado_em": fornecedor_jose.criado_em.isoformat("T"),
            "alterado_em": fornecedor_jose.alterado_em.isoformat("T"),
            "uuid": f'{fornecedor_jose.uuid}',
            "cpf_cnpj": fornecedor_jose.cpf_cnpj,
            "nome": fornecedor_jose.nome
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_fornecedor_filtro_qualquer_parte_cnpj(jwt_authenticated_client, fornecedor_industrias_teste):
    response = jwt_authenticated_client.get(f'/api/fornecedores/?cpf_cnpj=/0001', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "id": fornecedor_industrias_teste.id,
            "criado_em": fornecedor_industrias_teste.criado_em.isoformat("T"),
            "alterado_em": fornecedor_industrias_teste.alterado_em.isoformat("T"),
            "uuid": f'{fornecedor_industrias_teste.uuid}',
            "cpf_cnpj": fornecedor_industrias_teste.cpf_cnpj,
            "nome": fornecedor_industrias_teste.nome
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_fornecedor_filtro_qualquer_parte_nome(jwt_authenticated_client, fornecedor_jose):
    response = jwt_authenticated_client.get(f'/api/fornecedores/?nome=Jo', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "id": fornecedor_jose.id,
            "criado_em": fornecedor_jose.criado_em.isoformat("T"),
            "alterado_em": fornecedor_jose.alterado_em.isoformat("T"),
            "uuid": f'{fornecedor_jose.uuid}',
            "cpf_cnpj": fornecedor_jose.cpf_cnpj,
            "nome": fornecedor_jose.nome
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_fornecedor_filtro_qualquer_parte_cnpj_ou_nome(jwt_authenticated_client, fornecedor_industrias_teste):
    response = jwt_authenticated_client.get(f'/api/fornecedores/?cpf_cnpj=/0001&nome=d', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "id": fornecedor_industrias_teste.id,
            "criado_em": fornecedor_industrias_teste.criado_em.isoformat("T"),
            "alterado_em": fornecedor_industrias_teste.alterado_em.isoformat("T"),
            "uuid": f'{fornecedor_industrias_teste.uuid}',
            "cpf_cnpj": fornecedor_industrias_teste.cpf_cnpj,
            "nome": fornecedor_industrias_teste.nome
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

