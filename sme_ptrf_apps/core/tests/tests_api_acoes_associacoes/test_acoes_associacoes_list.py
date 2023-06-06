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
                    'data_de_encerramento': None,
                    'tooltip_data_encerramento': None,
                    'encerrada': False,
                    'informacoes': acao_associacao.associacao.tags_de_informacao,
                    'status_valores_reprogramados': acao_associacao.associacao.status_valores_reprogramados,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo,
                        'nome_dre': acao_associacao.associacao.unidade.nome_dre
                    },
                    'cnpj': acao_associacao.associacao.cnpj
                },
                'data_de_encerramento_associacao': None,
                'tooltip_associacao_encerrada': None,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios,
                    'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                    "aceita_capital": acao_associacao.acao.aceita_capital,
                    "aceita_custeio": acao_associacao.acao.aceita_custeio,
                    "aceita_livre": acao_associacao.acao.aceita_livre
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
                    'data_de_encerramento': None,
                    'tooltip_data_encerramento': None,
                    'encerrada': False,
                    'informacoes': acao_associacao.associacao.tags_de_informacao,
                    'status_valores_reprogramados': acao_associacao.associacao.status_valores_reprogramados,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo,
                        'nome_dre': acao_associacao.associacao.unidade.nome_dre
                    },
                    'cnpj': acao_associacao.associacao.cnpj
                },
                'data_de_encerramento_associacao': None,
                'tooltip_associacao_encerrada': None,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios,
                    'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                    "aceita_capital": acao_associacao.acao.aceita_capital,
                    "aceita_custeio": acao_associacao.acao.aceita_custeio,
                    "aceita_livre": acao_associacao.acao.aceita_livre
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
                    'data_de_encerramento': None,
                    'tooltip_data_encerramento': None,
                    'encerrada': False,
                    'informacoes': acao_associacao.associacao.tags_de_informacao,
                    'status_valores_reprogramados': acao_associacao.associacao.status_valores_reprogramados,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo,
                        'nome_dre': acao_associacao.associacao.unidade.nome_dre
                    },
                    'cnpj': acao_associacao.associacao.cnpj
                },
                'data_de_encerramento_associacao': None,
                'tooltip_associacao_encerrada': None,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios,
                    'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                    "aceita_capital": acao_associacao.acao.aceita_capital,
                    "aceita_custeio": acao_associacao.acao.aceita_custeio,
                    "aceita_livre": acao_associacao.acao.aceita_livre
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
                    'data_de_encerramento': None,
                    'tooltip_data_encerramento': None,
                    'encerrada': False,
                    'informacoes': acao_associacao.associacao.tags_de_informacao,
                    'status_valores_reprogramados': acao_associacao.associacao.status_valores_reprogramados,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo,
                        'nome_dre': acao_associacao.associacao.unidade.nome_dre
                    },
                    'cnpj': acao_associacao.associacao.cnpj
                },
                'data_de_encerramento_associacao': None,
                'tooltip_associacao_encerrada': None,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios,
                    'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                    "aceita_capital": acao_associacao.acao.aceita_capital,
                    "aceita_custeio": acao_associacao.acao.aceita_custeio,
                    "aceita_livre": acao_associacao.acao.aceita_livre
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
                    'data_de_encerramento': None,
                    'tooltip_data_encerramento': None,
                    'encerrada': False,
                    'informacoes': acao_associacao.associacao.tags_de_informacao,
                    'status_valores_reprogramados': acao_associacao.associacao.status_valores_reprogramados,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo,
                        'nome_dre': acao_associacao.associacao.unidade.nome_dre
                    },
                    'cnpj': acao_associacao.associacao.cnpj
                },
                'data_de_encerramento_associacao': None,
                'tooltip_associacao_encerrada': None,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios,
                    'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                    "aceita_capital": acao_associacao.acao.aceita_capital,
                    "aceita_custeio": acao_associacao.acao.aceita_custeio,
                    "aceita_livre": acao_associacao.acao.aceita_livre
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
                    'data_de_encerramento': None,
                    'tooltip_data_encerramento': None,
                    'encerrada': False,
                    'informacoes': acao_associacao.associacao.tags_de_informacao,
                    'status_valores_reprogramados': acao_associacao.associacao.status_valores_reprogramados,
                    'unidade': {
                        'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                        'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                        'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo,
                        'nome_dre': acao_associacao.associacao.unidade.nome_dre
                    },
                    'cnpj': acao_associacao.associacao.cnpj
                },
                'data_de_encerramento_associacao': None,
                'tooltip_associacao_encerrada': None,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios,
                    'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                    "aceita_capital": acao_associacao.acao.aceita_capital,
                    "aceita_custeio": acao_associacao.acao.aceita_custeio,
                    "aceita_livre": acao_associacao.acao.aceita_livre
                },
                'status': acao_associacao.status,
                'criado_em': acao_associacao.criado_em.isoformat("T"),
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_list_associacoes_por_associacoes_encerradas_e_nao_encerradas(jwt_authenticated_client_a,
                                                                          acao_associacao_charli_bravo_000086_x,
                                                                          acao_associacao_charli_bingo_000086_x,
                                                                          acao_x
                                                                        ):

    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?filtro_informacoes=ENCERRADAS,NAO_ENCERRADAS',
                                              content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{acao_associacao_charli_bingo_000086_x.uuid}',
            'id': acao_associacao_charli_bingo_000086_x.id,
            'associacao': {
                'uuid': f'{acao_associacao_charli_bingo_000086_x.associacao.uuid}',
                'nome': acao_associacao_charli_bingo_000086_x.associacao.nome,
                'data_de_encerramento': acao_associacao_charli_bingo_000086_x.associacao.data_de_encerramento.strftime("%Y-%m-%d"),
                'tooltip_data_encerramento': acao_associacao_charli_bingo_000086_x.associacao.tooltip_data_encerramento,
                'encerrada': acao_associacao_charli_bingo_000086_x.associacao.encerrada,
                'informacoes': acao_associacao_charli_bingo_000086_x.associacao.tags_de_informacao,
                'status_valores_reprogramados': acao_associacao_charli_bingo_000086_x.associacao.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{acao_associacao_charli_bingo_000086_x.associacao.unidade.uuid}',
                    'codigo_eol': acao_associacao_charli_bingo_000086_x.associacao.unidade.codigo_eol,
                    'nome_com_tipo': acao_associacao_charli_bingo_000086_x.associacao.unidade.nome_com_tipo,
                    'nome_dre': acao_associacao_charli_bingo_000086_x.associacao.unidade.nome_dre
                },
                'cnpj': acao_associacao_charli_bingo_000086_x.associacao.cnpj
            },
            'data_de_encerramento_associacao': acao_associacao_charli_bingo_000086_x.associacao.data_de_encerramento.strftime("%Y-%m-%d"),
            'tooltip_associacao_encerrada': acao_associacao_charli_bingo_000086_x.associacao.tooltip_data_encerramento,
            'acao': {
                'id': acao_associacao_charli_bingo_000086_x.acao.id,
                'uuid': f'{acao_associacao_charli_bingo_000086_x.acao.uuid}',
                'nome': acao_associacao_charli_bingo_000086_x.acao.nome,
                'e_recursos_proprios': acao_associacao_charli_bingo_000086_x.acao.e_recursos_proprios,
                'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                "aceita_capital": acao_associacao_charli_bingo_000086_x.acao.aceita_capital,
                "aceita_custeio": acao_associacao_charli_bingo_000086_x.acao.aceita_custeio,
                "aceita_livre": acao_associacao_charli_bingo_000086_x.acao.aceita_livre
            },
            'status': acao_associacao_charli_bingo_000086_x.status,
            'criado_em': acao_associacao_charli_bingo_000086_x.criado_em.isoformat("T"),
        },
        {
            'uuid': f'{acao_associacao_charli_bravo_000086_x.uuid}',
            'id': acao_associacao_charli_bravo_000086_x.id,
            'associacao': {
                'uuid': f'{acao_associacao_charli_bravo_000086_x.associacao.uuid}',
                'nome': acao_associacao_charli_bravo_000086_x.associacao.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': acao_associacao_charli_bravo_000086_x.associacao.encerrada,
                'informacoes': acao_associacao_charli_bravo_000086_x.associacao.tags_de_informacao,
                'status_valores_reprogramados': acao_associacao_charli_bravo_000086_x.associacao.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{acao_associacao_charli_bravo_000086_x.associacao.unidade.uuid}',
                    'codigo_eol': acao_associacao_charli_bravo_000086_x.associacao.unidade.codigo_eol,
                    'nome_com_tipo': acao_associacao_charli_bravo_000086_x.associacao.unidade.nome_com_tipo,
                    'nome_dre': acao_associacao_charli_bravo_000086_x.associacao.unidade.nome_dre
                },
                'cnpj': acao_associacao_charli_bravo_000086_x.associacao.cnpj
            },
            'data_de_encerramento_associacao': None,
            'tooltip_associacao_encerrada': None,
            'acao': {
                'id': acao_associacao_charli_bravo_000086_x.acao.id,
                'uuid': f'{acao_associacao_charli_bravo_000086_x.acao.uuid}',
                'nome': acao_associacao_charli_bravo_000086_x.acao.nome,
                'e_recursos_proprios': acao_associacao_charli_bravo_000086_x.acao.e_recursos_proprios,
                'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                "aceita_capital": acao_associacao_charli_bravo_000086_x.acao.aceita_capital,
                "aceita_custeio": acao_associacao_charli_bravo_000086_x.acao.aceita_custeio,
                "aceita_livre": acao_associacao_charli_bravo_000086_x.acao.aceita_livre
            },
            'status': acao_associacao_charli_bravo_000086_x.status,
            'criado_em': acao_associacao_charli_bravo_000086_x.criado_em.isoformat("T"),
        },
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_list_associacoes_por_associacoes_somente_encerradas(jwt_authenticated_client_a,
                                                                 acao_associacao_charli_bingo_000086_x,
                                                                 acao_x
                                                                ):

    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?filtro_informacoes=ENCERRADAS',
                                              content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{acao_associacao_charli_bingo_000086_x.uuid}',
            'id': acao_associacao_charli_bingo_000086_x.id,
            'associacao': {
                'uuid': f'{acao_associacao_charli_bingo_000086_x.associacao.uuid}',
                'nome': acao_associacao_charli_bingo_000086_x.associacao.nome,
                'data_de_encerramento': acao_associacao_charli_bingo_000086_x.associacao.data_de_encerramento.strftime("%Y-%m-%d"),
                'tooltip_data_encerramento': acao_associacao_charli_bingo_000086_x.associacao.tooltip_data_encerramento,
                'encerrada': acao_associacao_charli_bingo_000086_x.associacao.encerrada,
                'informacoes': acao_associacao_charli_bingo_000086_x.associacao.tags_de_informacao,
                'status_valores_reprogramados': acao_associacao_charli_bingo_000086_x.associacao.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{acao_associacao_charli_bingo_000086_x.associacao.unidade.uuid}',
                    'codigo_eol': acao_associacao_charli_bingo_000086_x.associacao.unidade.codigo_eol,
                    'nome_com_tipo': acao_associacao_charli_bingo_000086_x.associacao.unidade.nome_com_tipo,
                    'nome_dre': acao_associacao_charli_bingo_000086_x.associacao.unidade.nome_dre
                },
                'cnpj': acao_associacao_charli_bingo_000086_x.associacao.cnpj
            },
            'data_de_encerramento_associacao': acao_associacao_charli_bingo_000086_x.associacao.data_de_encerramento.strftime("%Y-%m-%d"),
            'tooltip_associacao_encerrada': acao_associacao_charli_bingo_000086_x.associacao.tooltip_data_encerramento,
            'acao': {
                'id': acao_associacao_charli_bingo_000086_x.acao.id,
                'uuid': f'{acao_associacao_charli_bingo_000086_x.acao.uuid}',
                'nome': acao_associacao_charli_bingo_000086_x.acao.nome,
                'e_recursos_proprios': acao_associacao_charli_bingo_000086_x.acao.e_recursos_proprios,
                'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                "aceita_capital": acao_associacao_charli_bingo_000086_x.acao.aceita_capital,
                "aceita_custeio": acao_associacao_charli_bingo_000086_x.acao.aceita_custeio,
                "aceita_livre": acao_associacao_charli_bingo_000086_x.acao.aceita_livre
            },
            'status': acao_associacao_charli_bingo_000086_x.status,
            'criado_em': acao_associacao_charli_bingo_000086_x.criado_em.isoformat("T"),
        }
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_list_associacoes_por_associacoes_somente_nao_encerradas(jwt_authenticated_client_a,
                                                                     acao_associacao_charli_bravo_000086_x,
                                                                     acao_x
                                                                    ):

    response = jwt_authenticated_client_a.get(f'/api/acoes-associacoes/?filtro_informacoes=NAO_ENCERRADAS',
                                              content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{acao_associacao_charli_bravo_000086_x.uuid}',
            'id': acao_associacao_charli_bravo_000086_x.id,
            'associacao': {
                'uuid': f'{acao_associacao_charli_bravo_000086_x.associacao.uuid}',
                'nome': acao_associacao_charli_bravo_000086_x.associacao.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': acao_associacao_charli_bravo_000086_x.associacao.encerrada,
                'informacoes': acao_associacao_charli_bravo_000086_x.associacao.tags_de_informacao,
                'status_valores_reprogramados': acao_associacao_charli_bravo_000086_x.associacao.status_valores_reprogramados,
                'unidade': {
                    'uuid': f'{acao_associacao_charli_bravo_000086_x.associacao.unidade.uuid}',
                    'codigo_eol': acao_associacao_charli_bravo_000086_x.associacao.unidade.codigo_eol,
                    'nome_com_tipo': acao_associacao_charli_bravo_000086_x.associacao.unidade.nome_com_tipo,
                    'nome_dre': acao_associacao_charli_bravo_000086_x.associacao.unidade.nome_dre
                },
                'cnpj': acao_associacao_charli_bravo_000086_x.associacao.cnpj
            },
            'data_de_encerramento_associacao': None,
            'tooltip_associacao_encerrada': None,
            'acao': {
                'id': acao_associacao_charli_bravo_000086_x.acao.id,
                'uuid': f'{acao_associacao_charli_bravo_000086_x.acao.uuid}',
                'nome': acao_associacao_charli_bravo_000086_x.acao.nome,
                'e_recursos_proprios': acao_associacao_charli_bravo_000086_x.acao.e_recursos_proprios,
                'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
                "aceita_capital": acao_associacao_charli_bravo_000086_x.acao.aceita_capital,
                "aceita_custeio": acao_associacao_charli_bravo_000086_x.acao.aceita_custeio,
                "aceita_livre": acao_associacao_charli_bravo_000086_x.acao.aceita_livre
            },
            'status': acao_associacao_charli_bravo_000086_x.status,
            'criado_em': acao_associacao_charli_bravo_000086_x.criado_em.isoformat("T"),
        },
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
