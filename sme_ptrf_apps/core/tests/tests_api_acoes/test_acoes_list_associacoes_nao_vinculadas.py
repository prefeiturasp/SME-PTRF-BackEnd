import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_acoes_list_associacoes_nao_vinculadas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'data_de_encerramento': None,
            'tooltip_data_encerramento': None,
            'encerrada': False,
            'informacoes': associacao_eco_delta_000087.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000087.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000087.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000087.cnpj
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_acoes_list_associacoes_nao_vinculadas_encerradas_e_nao_encerradas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   associacao_eco_delta_000088,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas/?filtro_informacoes=ENCERRADAS,NAO_ENCERRADAS', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'data_de_encerramento': None,
            'tooltip_data_encerramento': None,
            'encerrada': False,
            'informacoes': associacao_eco_delta_000087.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000087.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000087.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000087.cnpj
        },
        {
            'uuid': f'{associacao_eco_delta_000088.uuid}',
            'nome': associacao_eco_delta_000088.nome,
            'data_de_encerramento': associacao_eco_delta_000088.data_de_encerramento.strftime("%Y-%m-%d"),
            'tooltip_data_encerramento': associacao_eco_delta_000088.tooltip_data_encerramento,
            'encerrada': associacao_eco_delta_000088.encerrada,
            'informacoes': associacao_eco_delta_000088.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000088.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000088.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000088.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000088.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000088.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000088.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_acoes_list_associacoes_nao_vinculadas_somente_nao_encerradas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   associacao_eco_delta_000088,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas/?filtro_informacoes=NAO_ENCERRADAS', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'data_de_encerramento': None,
            'tooltip_data_encerramento': None,
            'encerrada': False,
            'informacoes': associacao_eco_delta_000087.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000087.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000087.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000087.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_acoes_list_associacoes_nao_vinculadas_somente_encerradas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   associacao_eco_delta_000088,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas/?filtro_informacoes=NAO_ENCERRADAS', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'data_de_encerramento': None,
            'tooltip_data_encerramento': None,
            'encerrada': False,
            'informacoes': associacao_eco_delta_000087.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000087.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000087.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000087.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_acoes_list_associacoes_nao_vinculadas_por_nome(jwt_authenticated_client_a,
                                                            acao_x,
                                                            acao_y,
                                                            associacao_charli_bravo_000086,
                                                            associacao_eco_delta_000087,
                                                            acao_associacao_charli_bravo_000086_x,
                                                            acao_associacao_eco_delta_000087_x
                                                            ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas-por-nome/delta/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'data_de_encerramento': None,
            'encerrada': False,
            'informacoes': associacao_eco_delta_000087.tags_de_informacao,
            'tooltip_data_encerramento': None,
            'status_valores_reprogramados': associacao_eco_delta_000087.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000087.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000087.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_acoes_list_associacoes_nao_vinculadas_por_nome_e_encerradas_e_nao_encerradas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   associacao_eco_delta_000088,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas-por-nome/delta/?filtro_informacoes=ENCERRADAS,NAO_ENCERRADAS', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'data_de_encerramento': None,
            'tooltip_data_encerramento': None,
            'encerrada': False,
            'informacoes': associacao_eco_delta_000087.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000087.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000087.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000087.cnpj
        },
        {
            'uuid': f'{associacao_eco_delta_000088.uuid}',
            'nome': associacao_eco_delta_000088.nome,
            'data_de_encerramento': associacao_eco_delta_000088.data_de_encerramento.strftime("%Y-%m-%d"),
            'tooltip_data_encerramento': associacao_eco_delta_000088.tooltip_data_encerramento,
            'encerrada': associacao_eco_delta_000088.encerrada,
            'informacoes': associacao_eco_delta_000088.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000088.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000088.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000088.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000088.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000088.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000088.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_acoes_list_associacoes_nao_vinculadas_por_nome_e_somente_nao_encerradas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   associacao_eco_delta_000088,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas-por-nome/delta/?filtro_informacoes=NAO_ENCERRADAS', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000087.uuid}',
            'nome': associacao_eco_delta_000087.nome,
            'data_de_encerramento': None,
            'tooltip_data_encerramento': None,
            'encerrada': False,
            'informacoes': associacao_eco_delta_000087.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000087.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000087.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000087.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000087.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000087.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000087.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_api_acoes_list_associacoes_nao_vinculadas_por_nome_e_somente_encerradas(jwt_authenticated_client_a,
                                                   acao_x,
                                                   acao_y,
                                                   associacao_charli_bravo_000086,
                                                   associacao_eco_delta_000087,
                                                   associacao_eco_delta_000088,
                                                   acao_associacao_charli_bravo_000086_y,
                                                   acao_associacao_charli_bravo_000086_x,
                                                   acao_associacao_eco_delta_000087_x
                                                   ):
    response = jwt_authenticated_client_a.get(f'/api/acoes/{acao_y.uuid}/associacoes-nao-vinculadas-por-nome/delta/?filtro_informacoes=ENCERRADAS', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': f'{associacao_eco_delta_000088.uuid}',
            'nome': associacao_eco_delta_000088.nome,
            'data_de_encerramento': associacao_eco_delta_000088.data_de_encerramento.strftime("%Y-%m-%d"),
            'tooltip_data_encerramento': associacao_eco_delta_000088.tooltip_data_encerramento,
            'encerrada': associacao_eco_delta_000088.encerrada,
            'informacoes': associacao_eco_delta_000088.tags_de_informacao,
            'status_valores_reprogramados': associacao_eco_delta_000088.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{associacao_eco_delta_000088.unidade.uuid}',
                'codigo_eol': associacao_eco_delta_000088.unidade.codigo_eol,
                'nome_com_tipo': associacao_eco_delta_000088.unidade.nome_com_tipo,
                'nome_dre': associacao_eco_delta_000088.unidade.nome_dre
            },
            'cnpj': associacao_eco_delta_000088.cnpj
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
