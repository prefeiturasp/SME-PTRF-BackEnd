import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

@pytest.fixture
def payload_despesa_rateio_com_conta_nao_iniciada(
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    especificacao_material_servico,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2018-12-31",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2018-12-31",
        "valor_total": 1000.00,
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 1000.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 500.00,
                "numero_processo_incorporacao_capital": "6234673223462364632"
            }
        ]
    }
    return payload


@pytest.fixture
def payload_despesa_rateio_com_conta_encerrada(
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao_inativa,
    acao_associacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    especificacao_material_servico,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2019-10-02",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2019-10-02",
        "valor_total": 1000.00,
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao_inativa.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 1000.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 500.00,
                "numero_processo_incorporacao_capital": "6234673223462364632"
            }
        ]
    }
    return payload

@pytest.fixture
def payload_despesa_rateio_imposto_com_conta_nao_iniciada(
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    especificacao_material_servico,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2019-05-01",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2019-05-01",
        "valor_total": 1000.00,
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 1000.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 500.00,
                "numero_processo_incorporacao_capital": "6234673223462364632"
            }
        ],
        "despesas_impostos": [
            {
                "associacao": f'{associacao.uuid}',
                "tipo_documento": tipo_documento.id,
                "data_transacao": "2018-12-31",
                "tipo_transacao": tipo_transacao.id,

                "rateios": [{
                    "tipo_custeio": tipo_custeio.id,
                    "especificacao_material_servico": especificacao_material_servico.id,
                    "acao_associacao": f"{acao_associacao.uuid}",
                    "aplicacao_recurso": "CUSTEIO",
                    "associacao": f'{associacao.uuid}',
                    "conta_associacao": f"{conta_associacao.uuid}",
                    "escolha_tags": "nao",
                    "numero_processo_incorporacao_capital": "",
                    "quantidade_itens_capital": 0,
                    "valor_item_capital": 0,
                    "valor_original": 222,
                    "valor_rateio": 222
                }]
            }
        ],
    }
    return payload

@pytest.fixture
def payload_despesa_rateio_imposto_com_conta_encerrada(
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao_inativa,
    acao_associacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    especificacao_material_servico,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2018-05-01",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2019-05-01",
        "valor_total": 1000.00,
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao_inativa.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 1000.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 500.00,
                "numero_processo_incorporacao_capital": "6234673223462364632"
            }
        ],
        "despesas_impostos": [
            {
                "associacao": f'{associacao.uuid}',
                "tipo_documento": tipo_documento.id,
                "data_transacao": "2019-10-02",
                "tipo_transacao": tipo_transacao.id,

                "rateios": [{
                    "tipo_custeio": tipo_custeio.id,
                    "especificacao_material_servico": especificacao_material_servico.id,
                    "acao_associacao": f"{acao_associacao.uuid}",
                    "aplicacao_recurso": "CUSTEIO",
                    "associacao": f'{associacao.uuid}',
                    "conta_associacao": f"{conta_associacao_inativa.uuid}",
                    "escolha_tags": "nao",
                    "numero_processo_incorporacao_capital": "",
                    "quantidade_itens_capital": 0,
                    "valor_item_capital": 0,
                    "valor_original": 222,
                    "valor_rateio": 222
                }]
            }
        ],
    }
    return payload

def test_api_post_despesa_rateio_com_conta_nao_iniciada(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_rateio_com_conta_nao_iniciada
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_rateio_com_conta_nao_iniciada), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert 'mensagem' in response.json()
    assert "Um ou mais rateios possuem conta com data de início posterior à data de transação." in response.json()['mensagem']

def test_api_post_despesa_rateio_imposto_com_conta_nao_iniciada(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_rateio_imposto_com_conta_nao_iniciada
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_rateio_imposto_com_conta_nao_iniciada), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert 'mensagem' in response.json()
    assert "Um ou mais rateios de imposto possuem conta com data de início posterior à data de transação." in response.json()['mensagem']

def test_api_post_despesa_rateio_com_conta_encerrada_antes_da_data_transacao(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao_inativa,
    solicitacao_encerramento_conta_associacao,
    payload_despesa_rateio_com_conta_encerrada
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_rateio_com_conta_encerrada), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert 'mensagem' in response.json()
    assert "Um ou mais rateios possuem conta com data de encerramento anterior à data de transação." in response.json()['mensagem']

def test_api_post_despesa_rateio_imposto_com_conta_encerrada_antes_da_data_transacao(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao_inativa,
    solicitacao_encerramento_conta_associacao,
    payload_despesa_rateio_imposto_com_conta_encerrada
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_rateio_imposto_com_conta_encerrada), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert 'mensagem' in response.json()
    assert "Um ou mais rateios de imposto possuem conta com data de encerramento anterior à data de transação." in response.json()['mensagem']
