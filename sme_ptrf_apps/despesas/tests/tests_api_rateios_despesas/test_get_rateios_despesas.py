import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_rateios_despesas(jwt_authenticated_client, despesa, rateio_despesa_capital):
    response = jwt_authenticated_client.get('/api/rateios-despesas/', content_type='application/json')
    result = json.loads(response.content)

    results = [
        {
            "uuid": f'{rateio_despesa_capital.uuid}',
            "despesa": f'{despesa.uuid}',
            "numero_documento": despesa.numero_documento,
            "status_despesa": despesa.status,
            "especificacao_material_servico": {
                "id": rateio_despesa_capital.especificacao_material_servico.id,
                "descricao": rateio_despesa_capital.especificacao_material_servico.descricao,
                "aplicacao_recurso": rateio_despesa_capital.aplicacao_recurso,
                "tipo_custeio": rateio_despesa_capital.tipo_custeio.id
            },
            "data_documento": '2020-03-10',
            "aplicacao_recurso": rateio_despesa_capital.aplicacao_recurso,
            "acao_associacao": {
                "uuid": f'{rateio_despesa_capital.acao_associacao.uuid}',
                "id": rateio_despesa_capital.acao_associacao.id,
                "nome": rateio_despesa_capital.acao_associacao.acao.nome
            },
            "valor_total": despesa.valor_total,
            "conferido": rateio_despesa_capital.conferido,
            "cpf_cnpj_fornecedor": despesa.cpf_cnpj_fornecedor,
            "nome_fornecedor": despesa.nome_fornecedor,
            "tipo_documento_nome": despesa.tipo_documento.nome,
            "tipo_transacao_nome": despesa.tipo_transacao.nome,
            "data_transacao": '2020-03-10',
            'notificar_dias_nao_conferido': 0,
        },

    ]

    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
