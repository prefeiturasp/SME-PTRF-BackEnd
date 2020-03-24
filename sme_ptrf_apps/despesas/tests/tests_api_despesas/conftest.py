import pytest


@pytest.fixture
def payload_despesa_valida(
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
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": 11000.50,
        "valor_recursos_proprios": 1000.50,
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
