import json

import pytest
from rest_framework import status

from model_bakery import baker

from ...models import Despesa

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_despesa_com_motivos_pagamento_antecipado(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    motivo_pagamento_adiantado_01,
    motivo_pagamento_adiantado_02
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_transacao": "2022-03-10",
        "data_documento": "2022-03-10",
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "valor_total": 100,
        "valor_recursos_proprios": 0,
        "despesa_imposto": None,
        "motivos_pagamento_antecipado": [motivo_pagamento_adiantado_01.id, motivo_pagamento_adiantado_02.id],
        "outros_motivos_pagamento_antecipado": "Outros motivos pagamento antecipado",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": None,
                "acao_associacao": None,
                "aplicacao_recurso": None,
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 100,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 100,
                "numero_processo_incorporacao_capital": ""
            }
        ]
    }
    return payload


@pytest.fixture
def payload_despesa_sem_motivos_pagamento_antecipado_e_data_transacao_menor_que_data_documento_devo_retornar_excecao(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    motivo_pagamento_adiantado_01,
    motivo_pagamento_adiantado_02
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_transacao": "2022-03-09",
        "data_documento": "2022-03-10",
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "valor_total": 100,
        "valor_recursos_proprios": 0,
        "despesa_imposto": None,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": None,
                "acao_associacao": None,
                "aplicacao_recurso": None,
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 100,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 100,
                "numero_processo_incorporacao_capital": ""
            }
        ]
    }
    return payload


@pytest.fixture
def despesa_update_data_transacao_maior_ou_igual_data_documento_e_deve_apagar_motivos_pagamento_antecipado(
    associacao,
    motivo_pagamento_adiantado_01,
    motivo_pagamento_adiantado_02,
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        tipo_documento=None,
        tipo_transacao=None,
        numero_documento="",
        data_documento="2022-03-10",
        cpf_cnpj_fornecedor="",
        nome_fornecedor="",
        data_transacao="2022-03-10",
        valor_total=100,
        valor_recursos_proprios=0,
        motivos_pagamento_antecipado=[motivo_pagamento_adiantado_01, motivo_pagamento_adiantado_02],
        outros_motivos_pagamento_antecipado="Este é o motivo de pagamento antecipado",
    )


def test_put_despesa_update_data_transacao_maior_ou_igual_data_documento_e_deve_apagar_motivos_pagamento_antecipado(
    jwt_authenticated_client_d,
    motivo_pagamento_adiantado_01,
    motivo_pagamento_adiantado_02,
    despesa_update_data_transacao_maior_ou_igual_data_documento_e_deve_apagar_motivos_pagamento_antecipado,
    payload_despesa_com_motivos_pagamento_antecipado,

):
    response = jwt_authenticated_client_d.put(f'/api/despesas/{despesa_update_data_transacao_maior_ou_igual_data_documento_e_deve_apagar_motivos_pagamento_antecipado.uuid}/', data=json.dumps(payload_despesa_com_motivos_pagamento_antecipado),
                          content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert result['motivos_pagamento_antecipado'] == []
    assert result['outros_motivos_pagamento_antecipado'] == ""


def test_post_despesa_sem_motivos_pagamento_antecipado_e_data_transacao_menor_que_data_documento_devo_retornar_excecao(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_sem_motivos_pagamento_antecipado_e_data_transacao_menor_que_data_documento_devo_retornar_excecao,
    jwt_authenticated_client_d,
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(
        payload_despesa_sem_motivos_pagamento_antecipado_e_data_transacao_menor_que_data_documento_devo_retornar_excecao),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    resultado_esperado = {
        "detail": "Quando a Data da transação for menor que a Data do Documento é necessário enviar os motivos do pagamento antecipado"
    }

    assert result == resultado_esperado
