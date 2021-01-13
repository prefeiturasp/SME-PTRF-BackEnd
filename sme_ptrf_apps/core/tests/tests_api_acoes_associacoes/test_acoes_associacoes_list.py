import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_acoes_associacoes_todas(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x,
    acao_associacao_charli_bravo_000086_y,
    acao_associacao_eco_delta_000087_x
):
    response = jwt_authenticated_client_a.get('/api/acoes-associacoes/', content_type='application/json')
    result = json.loads(response.content)

    esperados = [acao_associacao_charli_bravo_000086_x, acao_associacao_charli_bravo_000086_y,
                 acao_associacao_eco_delta_000087_x]

    resultado_esperado = []
    for acao_associacao in esperados:
        resultado_esperado.append(
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'associacao': {
                    'uuid': f'{acao_associacao.associacao.uuid}',
                    'nome': acao_associacao.associacao.nome,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo
                    },
                    'status_regularidade': acao_associacao.associacao.status_regularidade,
                },
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios
                },
                'status': acao_associacao.status,
                'criado_em': acao_associacao.criado_em.isoformat("T"),
            }
        )

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_associacoes_pelo_nome_associacao(jwt_authenticated_client_a,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?nome=char', content_type='application/json')
    result = json.loads(response.content)

    esperados = [acao_associacao_charli_bravo_000086_x, acao_associacao_charli_bravo_000086_y]

    resultado_esperado = []
    for acao_associacao in esperados:
        resultado_esperado.append(
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'associacao': {
                    'uuid': f'{acao_associacao.associacao.uuid}',
                    'nome': acao_associacao.associacao.nome,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo
                    },
                    'status_regularidade': acao_associacao.associacao.status_regularidade,
                },
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios
                },
                'status': acao_associacao.status,
                'criado_em': acao_associacao.criado_em.isoformat("T"),
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_associacoes_pelo_nome_escola(jwt_authenticated_client_a,
                                               acao_associacao_charli_bravo_000086_x,
                                               acao_associacao_charli_bravo_000086_y,
                                               acao_associacao_eco_delta_000087_x
                                               ):
    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?nome=brav', content_type='application/json')
    result = json.loads(response.content)

    esperados = [acao_associacao_charli_bravo_000086_x, acao_associacao_charli_bravo_000086_y]

    resultado_esperado = []
    for acao_associacao in esperados:
        resultado_esperado.append(
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'associacao': {
                    'uuid': f'{acao_associacao.associacao.uuid}',
                    'nome': acao_associacao.associacao.nome,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo
                    },
                    'status_regularidade': acao_associacao.associacao.status_regularidade,
                },
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios
                },
                'status': acao_associacao.status,
                'criado_em': acao_associacao.criado_em.isoformat("T"),
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_associacoes_pelo_eol_escola(jwt_authenticated_client_a,
                                              acao_associacao_charli_bravo_000086_x,
                                              acao_associacao_charli_bravo_000086_y,
                                              acao_associacao_eco_delta_000087_x
                                              ):
    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?nome=86', content_type='application/json')
    result = json.loads(response.content)

    esperados = [acao_associacao_charli_bravo_000086_x, acao_associacao_charli_bravo_000086_y]

    resultado_esperado = []
    for acao_associacao in esperados:
        resultado_esperado.append(
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'associacao': {
                    'uuid': f'{acao_associacao.associacao.uuid}',
                    'nome': acao_associacao.associacao.nome,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo
                    },
                    'status_regularidade': acao_associacao.associacao.status_regularidade,
                },
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios
                },
                'status': acao_associacao.status,
                'criado_em': acao_associacao.criado_em.isoformat("T"),
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_associacoes_por_acao(jwt_authenticated_client_a,
                                       acao_associacao_charli_bravo_000086_x,
                                       acao_associacao_charli_bravo_000086_y,
                                       acao_associacao_eco_delta_000087_x,
                                       acao_x
                                       ):
    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?acao__uuid={acao_x.uuid}',
                                              content_type='application/json')
    result = json.loads(response.content)

    esperados = [acao_associacao_charli_bravo_000086_x, acao_associacao_eco_delta_000087_x]

    resultado_esperado = []
    for acao_associacao in esperados:
        resultado_esperado.append(
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'associacao': {
                    'uuid': f'{acao_associacao.associacao.uuid}',
                    'nome': acao_associacao.associacao.nome,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo
                    },
                    'status_regularidade': acao_associacao.associacao.status_regularidade,
                },
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios
                },
                'status': acao_associacao.status,
                'criado_em': acao_associacao.criado_em.isoformat("T"),
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_associacoes_por_status(jwt_authenticated_client_a,
                                         acao_associacao_charli_bravo_000086_x,
                                         acao_associacao_charli_bravo_000086_y,
                                         acao_associacao_eco_delta_000087_x,
                                         acao_associacao_eco_delta_000087_y_inativa
                                         ):

    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?status=INATIVA',
                                              content_type='application/json')
    result = json.loads(response.content)

    esperados = [acao_associacao_eco_delta_000087_y_inativa]

    resultado_esperado = []
    for acao_associacao in esperados:
        resultado_esperado.append(
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'associacao': {
                    'uuid': f'{acao_associacao.associacao.uuid}',
                    'nome': acao_associacao.associacao.nome,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo
                    },
                    'status_regularidade': acao_associacao.associacao.status_regularidade,
                },
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios
                },
                'status': acao_associacao.status,
                'criado_em': acao_associacao.criado_em.isoformat("T"),
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
