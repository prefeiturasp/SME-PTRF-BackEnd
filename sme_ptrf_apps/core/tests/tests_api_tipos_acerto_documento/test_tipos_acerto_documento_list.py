import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_tipos_acerto_documento_todos(
    jwt_authenticated_client_a,
    tipo_acerto_documento_assinatura,
    tipo_acerto_documento_enviar,
    tipo_documento_prestacao_conta_ata,
    tipo_documento_prestacao_conta_relacao_bens
):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-documento/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': tipo_acerto_documento_assinatura.ativo,
            'categoria': tipo_acerto_documento_assinatura.categoria,
            'id': tipo_acerto_documento_assinatura.id,
            'nome': 'Enviar com assinatura',
            'uuid': f'{tipo_acerto_documento_assinatura.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_ata.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_ata.id,
                    'nome': tipo_documento_prestacao_conta_ata.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}'
                }
            ]
        },
        {
            'ativo': tipo_acerto_documento_enviar.ativo,
            'categoria': tipo_acerto_documento_enviar.categoria,
            'id': tipo_acerto_documento_enviar.id,
            'nome': 'Enviar o documento',
            'uuid': f'{tipo_acerto_documento_enviar.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_ata.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_ata.id,
                    'nome': tipo_documento_prestacao_conta_ata.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}'
                },
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_relacao_bens.id,
                    'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
                }
            ]
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_documento_filtro_nome(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01,
    tipo_acerto_documento_02,
    tipo_acerto_documento_03,
    tipo_documento_prestacao_conta_relacao_bens,
    tipo_documento_prestacao_conta_ata
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-documento/?nome=tes', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': tipo_acerto_documento_01.ativo,
            'categoria': tipo_acerto_documento_01.categoria,
            'id': tipo_acerto_documento_01.id,
            'nome': tipo_acerto_documento_01.nome,
            'uuid': f'{tipo_acerto_documento_01.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_relacao_bens.id,
                    'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
                }
            ]
        },
        {
            'ativo': tipo_acerto_documento_03.ativo,
            'categoria': tipo_acerto_documento_03.categoria,
            'id': tipo_acerto_documento_03.id,
            'nome': tipo_acerto_documento_03.nome,
            'uuid': f'{tipo_acerto_documento_03.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_ata.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_ata.id,
                    'nome': tipo_documento_prestacao_conta_ata.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}'
                }
            ]
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_documento_filtro_categoria(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01,
    tipo_acerto_documento_02,
    tipo_acerto_documento_03,
    tipo_documento_prestacao_conta_relacao_bens,
    tipo_documento_prestacao_conta_ata
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-documento/?categoria=INCLUSAO_CREDITO,INCLUSAO_GASTO', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': tipo_acerto_documento_01.ativo,
            'categoria': tipo_acerto_documento_01.categoria,
            'id': tipo_acerto_documento_01.id,
            'nome': tipo_acerto_documento_01.nome,
            'uuid': f'{tipo_acerto_documento_01.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_relacao_bens.id,
                    'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
                }
            ]
        },
        {
            'ativo': tipo_acerto_documento_02.ativo,
            'categoria': tipo_acerto_documento_02.categoria,
            'id': tipo_acerto_documento_02.id,
            'nome': tipo_acerto_documento_02.nome,
            'uuid': f'{tipo_acerto_documento_02.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_relacao_bens.id,
                    'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
                }
            ]
        },
        {
            'ativo': tipo_acerto_documento_03.ativo,
            'categoria': tipo_acerto_documento_03.categoria,
            'id': tipo_acerto_documento_03.id,
            'nome': tipo_acerto_documento_03.nome,
            'uuid': f'{tipo_acerto_documento_03.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_ata.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_ata.id,
                    'nome': tipo_documento_prestacao_conta_ata.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}'
                }
            ]
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_documento_filtro_ativo(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01,
    tipo_acerto_documento_02,
    tipo_acerto_documento_03,
    tipo_documento_prestacao_conta_relacao_bens,
    tipo_documento_prestacao_conta_ata
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-documento/?ativo=False', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': tipo_acerto_documento_03.ativo,
            'categoria': tipo_acerto_documento_03.categoria,
            'id': tipo_acerto_documento_03.id,
            'nome': tipo_acerto_documento_03.nome,
            'uuid': f'{tipo_acerto_documento_03.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_ata.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_ata.id,
                    'nome': tipo_documento_prestacao_conta_ata.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}'
                }
            ]
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_documento_filtro_documento_relacionado(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01,
    tipo_acerto_documento_02,
    tipo_acerto_documento_03,
    tipo_documento_prestacao_conta_relacao_bens,
    tipo_documento_prestacao_conta_ata
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-documento/?documento_relacionado={tipo_documento_prestacao_conta_relacao_bens.id}',
        content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': tipo_acerto_documento_01.ativo,
            'categoria': tipo_acerto_documento_01.categoria,
            'id': tipo_acerto_documento_01.id,
            'nome': tipo_acerto_documento_01.nome,
            'uuid': f'{tipo_acerto_documento_01.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_relacao_bens.id,
                    'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
                }
            ]
        },
        {
            'ativo': tipo_acerto_documento_02.ativo,
            'categoria': tipo_acerto_documento_02.categoria,
            'id': tipo_acerto_documento_02.id,
            'nome': tipo_acerto_documento_02.nome,
            'uuid': f'{tipo_acerto_documento_02.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_relacao_bens.id,
                    'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
                }
            ]
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_documento_por_tipo_documento(
    jwt_authenticated_client_a,
    tipo_acerto_documento_assinatura,
    tipo_acerto_documento_enviar,
    tipo_documento_prestacao_conta_relacao_bens,
    tipo_documento_prestacao_conta_ata
):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-documento/?tipos_documento_prestacao__uuid={tipo_documento_prestacao_conta_relacao_bens.uuid}', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': tipo_acerto_documento_enviar.ativo,
            'categoria': tipo_acerto_documento_enviar.categoria,
            'id': tipo_acerto_documento_enviar.id,
            'nome': 'Enviar o documento',
            'uuid': f'{tipo_acerto_documento_enviar.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_ata.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_ata.id,
                    'nome': tipo_documento_prestacao_conta_ata.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}'
                },
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_relacao_bens.id,
                    'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
                }
            ]
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_documento_filtro_composto(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01,
    tipo_acerto_documento_02,
    tipo_acerto_documento_03,
    tipo_documento_prestacao_conta_relacao_bens,
    tipo_documento_prestacao_conta_ata
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-documento/?categoria=INCLUSAO_CREDITO&nome=1', content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'ativo': tipo_acerto_documento_03.ativo,
            'categoria': tipo_acerto_documento_03.categoria,
            'id': tipo_acerto_documento_03.id,
            'nome': tipo_acerto_documento_03.nome,
            'uuid': f'{tipo_acerto_documento_03.uuid}',
            'tipos_documento_prestacao': [
                {
                    'documento_por_conta': tipo_documento_prestacao_conta_ata.documento_por_conta,
                    'id': tipo_documento_prestacao_conta_ata.id,
                    'nome': tipo_documento_prestacao_conta_ata.nome,
                    'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}'
                }
            ]
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
