import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_membros_comissoes_todos(
    jwt_authenticated_client_dre,
    comissao_a, comissao_b,
    dre_x, dre_y,
    membro_beto_comissao_a_b_dre_x, membro_jose_comissao_a_b_dre_y, membro_alex_comissao_a_dre_x
):
    response = jwt_authenticated_client_dre.get(f'/api/membros-comissoes/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{membro_alex_comissao_a_dre_x.uuid}',
            "rf": membro_alex_comissao_a_dre_x.rf,
            "nome": membro_alex_comissao_a_dre_x.nome,
            "email": membro_alex_comissao_a_dre_x.email,
            "qtd_comissoes": membro_alex_comissao_a_dre_x.qtd_comissoes,
            "dre": f'{membro_alex_comissao_a_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                }
            ],

        },
        {
            "uuid": f'{membro_beto_comissao_a_b_dre_x.uuid}',
            "rf": membro_beto_comissao_a_b_dre_x.rf,
            "nome": membro_beto_comissao_a_b_dre_x.nome,
            "email": membro_beto_comissao_a_b_dre_x.email,
            "qtd_comissoes": membro_beto_comissao_a_b_dre_x.qtd_comissoes,
            "dre": f'{membro_beto_comissao_a_b_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },
        {
            "uuid": f'{membro_jose_comissao_a_b_dre_y.uuid}',
            "rf": membro_jose_comissao_a_b_dre_y.rf,
            "nome": membro_jose_comissao_a_b_dre_y.nome,
            "email": membro_jose_comissao_a_b_dre_y.email,
            "qtd_comissoes": membro_jose_comissao_a_b_dre_y.qtd_comissoes,
            "dre": f'{membro_jose_comissao_a_b_dre_y.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_membros_comissoes_por_dre(
    jwt_authenticated_client_dre,
    comissao_a, comissao_b,
    dre_x, dre_y,
    membro_beto_comissao_a_b_dre_x, membro_jose_comissao_a_b_dre_y, membro_alex_comissao_a_dre_x
):
    response = jwt_authenticated_client_dre.get(
        f'/api/membros-comissoes/?dre__uuid={dre_x.uuid}',
        content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{membro_alex_comissao_a_dre_x.uuid}',
            "rf": membro_alex_comissao_a_dre_x.rf,
            "nome": membro_alex_comissao_a_dre_x.nome,
            "email": membro_alex_comissao_a_dre_x.email,
            "qtd_comissoes": membro_alex_comissao_a_dre_x.qtd_comissoes,
            "dre": f'{membro_alex_comissao_a_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                }
            ],
        },
        {
            "uuid": f'{membro_beto_comissao_a_b_dre_x.uuid}',
            "rf": membro_beto_comissao_a_b_dre_x.rf,
            "nome": membro_beto_comissao_a_b_dre_x.nome,
            "email": membro_beto_comissao_a_b_dre_x.email,
            "qtd_comissoes": membro_beto_comissao_a_b_dre_x.qtd_comissoes,
            "dre": f'{membro_beto_comissao_a_b_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_membros_comissoes_por_rf(
    jwt_authenticated_client_dre,
    comissao_a, comissao_b,
    dre_x, dre_y,
    membro_beto_comissao_a_b_dre_x, membro_jose_comissao_a_b_dre_y, membro_alex_comissao_a_dre_x
):
    response = jwt_authenticated_client_dre.get(
        f'/api/membros-comissoes/?nome_ou_rf={membro_beto_comissao_a_b_dre_x.rf}',
        content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{membro_beto_comissao_a_b_dre_x.uuid}',
            "rf": membro_beto_comissao_a_b_dre_x.rf,
            "nome": membro_beto_comissao_a_b_dre_x.nome,
            "email": membro_beto_comissao_a_b_dre_x.email,
            "qtd_comissoes": membro_beto_comissao_a_b_dre_x.qtd_comissoes,
            "dre": f'{membro_beto_comissao_a_b_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_membros_comissoes_por_nome_ignorando_maisculas_minusculas_acentos(
    jwt_authenticated_client_dre,
    comissao_a, comissao_b,
    dre_x, dre_y,
    membro_beto_comissao_a_b_dre_x, membro_jose_comissao_a_b_dre_y, membro_alex_comissao_a_dre_x
):
    response = jwt_authenticated_client_dre.get(
        f'/api/membros-comissoes/?nome_ou_rf=ÉTO',
        content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{membro_beto_comissao_a_b_dre_x.uuid}',
            "rf": membro_beto_comissao_a_b_dre_x.rf,
            "nome": membro_beto_comissao_a_b_dre_x.nome,
            "email": membro_beto_comissao_a_b_dre_x.email,
            "qtd_comissoes": membro_beto_comissao_a_b_dre_x.qtd_comissoes,
            "dre": f'{membro_beto_comissao_a_b_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_membros_comissoes_por_dre_e_nome(
    jwt_authenticated_client_dre,
    comissao_a, comissao_b,
    dre_x, dre_y,
    membro_beto_comissao_a_b_dre_x, membro_jose_comissao_a_b_dre_y, membro_alex_comissao_a_dre_x
):
    # A letra 'o' existe em 'Beto' e 'José', mas apena so Beto é da DRE X.
    response = jwt_authenticated_client_dre.get(
        f'/api/membros-comissoes/?dre__uuid={dre_x.uuid}&nome_ou_rf=o',
        content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{membro_beto_comissao_a_b_dre_x.uuid}',
            "rf": membro_beto_comissao_a_b_dre_x.rf,
            "nome": membro_beto_comissao_a_b_dre_x.nome,
            "email": membro_beto_comissao_a_b_dre_x.email,
            "qtd_comissoes": membro_beto_comissao_a_b_dre_x.qtd_comissoes,
            "dre": f'{membro_beto_comissao_a_b_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_membros_comissoes_por_comissao(
    jwt_authenticated_client_dre,
    comissao_a, comissao_b,
    dre_x, dre_y,
    membro_beto_comissao_a_b_dre_x, membro_jose_comissao_a_b_dre_y, membro_alex_comissao_a_dre_x
):
    response = jwt_authenticated_client_dre.get(
        f'/api/membros-comissoes/?comissao_uuid={comissao_b.uuid}',
        content_type='application/json'
    )
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{membro_beto_comissao_a_b_dre_x.uuid}',
            "rf": membro_beto_comissao_a_b_dre_x.rf,
            "nome": membro_beto_comissao_a_b_dre_x.nome,
            "email": membro_beto_comissao_a_b_dre_x.email,
            "qtd_comissoes": membro_beto_comissao_a_b_dre_x.qtd_comissoes,
            "dre": f'{membro_beto_comissao_a_b_dre_x.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },
        {
            "uuid": f'{membro_jose_comissao_a_b_dre_y.uuid}',
            "rf": membro_jose_comissao_a_b_dre_y.rf,
            "nome": membro_jose_comissao_a_b_dre_y.nome,
            "email": membro_jose_comissao_a_b_dre_y.email,
            "qtd_comissoes": membro_jose_comissao_a_b_dre_y.qtd_comissoes,
            "dre": f'{membro_jose_comissao_a_b_dre_y.dre.uuid}',
            "comissoes": [
                {
                    'nome': 'A',
                    'uuid': f'{comissao_a.uuid}',
                    'id': comissao_a.id
                },
                {
                    'nome': 'B',
                    'uuid': f'{comissao_b.uuid}',
                    'id': comissao_b.id
                }
            ],
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
