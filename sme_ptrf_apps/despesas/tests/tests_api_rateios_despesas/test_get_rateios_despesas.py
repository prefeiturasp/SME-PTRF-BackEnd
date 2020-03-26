import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_rateios_despesas(client, despesa, rateio_despesa_capital):
    response = client.get('/api/rateios-despesas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        {
            "uuid": f'{rateio_despesa_capital.uuid}',
            "despesa": f'{despesa.uuid}',
            "numero_documento": despesa.numero_documento,
            "status_despesa": despesa.status,
            "especificacao_material_servico": {
                "id": despesa.especificacao_material_servico.id,
                "descricao": despesa.especificacao_material_servico.descricao,
                "aplicacao_recurso": rateio_despesa_capital.aplicacao_recurso,
                "tipo_custeio": rateio_despesa_capital.tipo_custeio.id
            },
            "data_documento": despesa.data_documento,
            "aplicacao_recurso": rateio_despesa_capital.aplicacao_recurso,
            "acao_associacao": {
                "uuid": rateio_despesa_capital.acao_associacao.uuid,
                "nome": rateio_despesa_capital.acao_associacao.acao.nome
            },
            "valor_total": despesa.valor_total
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_capital(client, json_especificacao_custeio_material,
                                                   json_especificacao_custeio_servico, json_especificacao_capital):
    response = client.get('/api/especificacoes/?aplicacao_recurso=CAPITAL', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_capital,

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_custeio(client, json_especificacao_custeio_material,
                                                   json_especificacao_custeio_servico, json_especificacao_capital):
    response = client.get('/api/especificacoes/?aplicacao_recurso=CUSTEIO', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_custeio_material,
        json_especificacao_custeio_servico,
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_api_get_especificacoes_com_filtro_custeio_servico(client, json_especificacao_custeio_material,
                                                           json_especificacao_custeio_servico,
                                                           json_especificacao_capital, tipo_custeio_servico):
    response = client.get(f'/api/especificacoes/?aplicacao_recurso=CUSTEIO&tipo_custeio={tipo_custeio_servico.id}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        json_especificacao_custeio_servico,
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
