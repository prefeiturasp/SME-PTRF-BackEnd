import json

import pytest
from rest_framework import status

from model_bakery import baker

from ...models import Despesa

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_despesa_com_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": "2022-03-10",
        "valor_total": 100,
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "despesas_impostos": [
            {
                "associacao": f'{associacao.uuid}',
                "tipo_documento": tipo_documento.id,
                "data_transacao": None,
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
def payload_despesa_remove_vinculo_com_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": "2022-03-10",
        "valor_total": 100,
        "valor_recursos_proprios": 0,
        "despesas_impostos": [],
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
def rateio_despesa_despesa_imposto(associacao, tipo_custeio, especificacao_material_servico, acao_associacao,
                                   conta_associacao, despesa_despesa_imposto):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_despesa_imposto,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        associacao=associacao,
        conta_associacao=conta_associacao,
        numero_processo_incorporacao_capital="",
        quantidade_itens_capital=0,
        valor_item_capital=0,
        valor_original=222,
        valor_rateio=222
    )


@pytest.fixture
def despesa_despesa_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
    )


@pytest.fixture
def rateio_despesa_com_imposto(associacao, despesa_com_imposto, conta_associacao, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_com_imposto,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=None,
        tipo_custeio=None,
        especificacao_material_servico=None,
        valor_rateio=100,
        quantidade_itens_capital=0,
        valor_item_capital=100,
        numero_processo_incorporacao_capital=""
    )


@pytest.fixture
def despesa_com_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    despesa_despesa_imposto
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        tipo_documento=None,
        tipo_transacao=None,
        numero_documento="",
        data_documento=None,
        cpf_cnpj_fornecedor="",
        nome_fornecedor="",
        data_transacao="2022-03-10",
        valor_total=100,
        valor_recursos_proprios=0,
        despesas_impostos=[despesa_despesa_imposto,]
    )


def test_retrieve_despesa_com_imposto(
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    uuid_despesa = despesa_com_imposto.uuid
    response = jwt_authenticated_client_d.get(f'/api/despesas/{uuid_despesa}/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result["uuid"] == str(despesa_com_imposto.uuid)


def test_put_despesa_remove_vinculo_com_a_despesa_de_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_remove_vinculo_com_imposto,
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    response = jwt_authenticated_client_d.put(
        f'/api/despesas/{despesa_com_imposto.uuid}/',
        data=json.dumps(payload_despesa_remove_vinculo_com_imposto),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert not despesa.despesas_impostos.exists()


def test_post_despesa_com_imposto_e_deve_criar_vinculo_com_a_despesa_de_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_com_imposto,
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_com_imposto),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid

    assert Despesa.objects.filter(uuid=despesa_despesa_imposto.uuid).exists()

    despesa_imposto = Despesa.objects.get(uuid=despesa_despesa_imposto.uuid)

    assert despesa_imposto.associacao.uuid == associacao.uuid


def test_delete_despesa_geradora_de_imposto_e_com_isso_deve_apagar_despesa_de_imposto_vinculada(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_remove_vinculo_com_imposto,
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    despesa_imposto_uuid = despesa_despesa_imposto.uuid
    despesa_com_imposto_uuid = despesa_com_imposto.uuid

    assert Despesa.objects.filter(uuid=despesa_com_imposto_uuid).exists()
    assert Despesa.objects.filter(uuid=despesa_imposto_uuid).exists()

    response = jwt_authenticated_client_d.delete(
        f'/api/despesas/{despesa_com_imposto.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Despesa.objects.filter(uuid=despesa_com_imposto_uuid).exists()
    assert not Despesa.objects.filter(uuid=despesa_imposto_uuid).exists()
