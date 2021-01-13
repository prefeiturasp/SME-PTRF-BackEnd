import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_acoes_associacoes_todas(
    jwt_authenticated_client_a,
    acao_associacao_charli_x,
    acao_associacao_charli_y,
    acao_associacao_eco_x
):
    response = jwt_authenticated_client_a.get('/api/acoes-associacoes/', content_type='application/json')
    result = json.loads(response.content)

    esperados = [acao_associacao_charli_x, acao_associacao_charli_y, acao_associacao_eco_x]

    resultado_esperado = []
    for acao_associacao in esperados:
        resultado_esperado.append(
            {
                'uuid': f'{acao_associacao.uuid}',
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
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios
                },
                'status': acao_associacao.status,
            }
        )

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_associacoes_pelo_nome_associacao_ignorando_acentos(jwt_authenticated_client_a,
                                                                     associacao_valenca_ceu_vassouras_dre_1,
                                                                     associacao_pinheiros_emef_mendes_dre_2):
    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?nome=valenca', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.uuid}',
            'nome': associacao_valenca_ceu_vassouras_dre_1.nome,
            'unidade': {
                'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.unidade.uuid}',
                'codigo_eol': associacao_valenca_ceu_vassouras_dre_1.unidade.codigo_eol,
                'nome_com_tipo': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_com_tipo
            },
            'status_regularidade': associacao_valenca_ceu_vassouras_dre_1.status_regularidade,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_associacoes_pelo_nome_escola(jwt_authenticated_client_a, associacao_valenca_ceu_vassouras_dre_1,
                                               associacao_pinheiros_emef_mendes_dre_2):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/?nome=vassouras', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.uuid}',
            'nome': associacao_valenca_ceu_vassouras_dre_1.nome,
            'unidade': {
                'uuid': f'{associacao_valenca_ceu_vassouras_dre_1.unidade.uuid}',
                'codigo_eol': associacao_valenca_ceu_vassouras_dre_1.unidade.codigo_eol,
                'nome_com_tipo': associacao_valenca_ceu_vassouras_dre_1.unidade.nome_com_tipo
            },
            'status_regularidade': associacao_valenca_ceu_vassouras_dre_1.status_regularidade,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

