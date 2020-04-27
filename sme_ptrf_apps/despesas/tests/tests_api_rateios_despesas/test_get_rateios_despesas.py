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
            "valor_total": despesa.valor_total
        },

    ]

    # TODO Voltar a paginar no back quando front estiver pronto para isso.
    # esperado = {
    #     'count': 1,
    #     'next': None,
    #     'previous': None,
    #     'results': results
    # }
    esperado = results

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
