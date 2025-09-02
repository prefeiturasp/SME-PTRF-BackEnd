import json
import pytest
from rest_framework import status
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

pytestmark = pytest.mark.django_db


def test_post_bem_produzido(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    associacao_1, despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    rateio_1 = rateio_despesa_factory(associacao=associacao_1, despesa=despesa_2025_1, valor_rateio=200)

    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 200
            },
        ],
        "itens": [
            {
                "num_processo_incorporacao": 985734857456873,
                "quantidade": 1,
                "valor_individual": 200,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.post('/api/bens-produzidos/', data=json.dumps(payload),
                                                 content_type='application/json')
    content = json.loads(response.content)

    assert content['uuid']
    assert content['associacao']
    assert content['status'] == BemProduzido.STATUS_COMPLETO
    assert response.status_code == status.HTTP_201_CREATED


def test_patch_bem_produzido_remove_itens_nao_enviados(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    bem_produzido_1,
    associacao_1, despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    # Criar despesa e rateio
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    rateio_1 = rateio_despesa_factory(associacao=associacao_1, despesa=despesa_2025_1, valor_rateio=400)
    
    # Primeiro, criar um bem produzido com 2 itens
    payload_inicial = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 400
            },
        ],
        "itens": [
            {
                "num_processo_incorporacao": "1234567890123456",
                "quantidade": 1,
                "valor_individual": 200,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            },
            {
                "num_processo_incorporacao": "6543210987654321",
                "quantidade": 1,
                "valor_individual": 200,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response_inicial = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos/{bem_produzido_1.uuid}/', 
                                                        data=json.dumps(payload_inicial),
                                                        content_type='application/json')
    
    assert response_inicial.status_code == status.HTTP_200_OK
    
    # Verificar que existem 2 itens
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoItem
    itens_iniciais = BemProduzidoItem.objects.filter(bem_produzido=bem_produzido_1)
    assert itens_iniciais.count() == 2
    
    # Agora enviar um patch com apenas 1 item (o primeiro)
    payload_atualizado = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 200
            },
        ],
        "itens": [
            {
                "uuid": str(itens_iniciais.first().uuid),  # Manter apenas o primeiro item
                "num_processo_incorporacao": "1234567890123456",
                "quantidade": 1,
                "valor_individual": 200,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response_atualizado = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos/{bem_produzido_1.uuid}/', 
                                                           data=json.dumps(payload_atualizado),
                                                           content_type='application/json')
    
    assert response_atualizado.status_code == status.HTTP_200_OK
    
    # Verificar que agora existe apenas 1 item
    itens_finais = BemProduzidoItem.objects.filter(bem_produzido=bem_produzido_1)
    assert itens_finais.count() == 1
    assert itens_finais.first().num_processo_incorporacao == "1234567890123456"


def test_patch_bem_produzido_com_especificacao_objeto(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    bem_produzido_1,
    associacao_1, despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    # Criar despesa e rateio
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    rateio_1 = rateio_despesa_factory(associacao=associacao_1, despesa=despesa_2025_1, valor_rateio=200)
    
    # Payload com especificação como objeto (simulando o que vem do frontend)
    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 200
            },
        ],
        "itens": [
            {
                "num_processo_incorporacao": "1234567890123456",
                "quantidade": 1,
                "valor_individual": 200,
                "especificacao_do_bem": {
                    "id": 6372,
                    "uuid": f"{especificacao_material_servico_1.uuid}",
                    "descricao": "Analisador de voltagem",
                    "aplicacao_recurso": "CAPITAL",
                    "tipo_custeio": None,
                    "tipo_custeio_objeto": None,
                    "ativa": False
                }
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos-rascunho/{bem_produzido_1.uuid}/', 
                                                data=json.dumps(payload),
                                                content_type='application/json')
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar se o item foi criado corretamente
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoItem
    itens = BemProduzidoItem.objects.filter(bem_produzido=bem_produzido_1)
    assert itens.count() == 1
    assert str(itens.first().especificacao_do_bem.uuid) == str(especificacao_material_servico_1.uuid)


def test_patch_bem_produzido(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    bem_produzido_1,
    associacao_1, despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    rateio_1 = rateio_despesa_factory(associacao=associacao_1, despesa=despesa_2025_1, valor_rateio=200)

    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 200
            },
        ],
        "itens": [
            {
                "num_processo_incorporacao": 985734857456873,
                "quantidade": 1,
                "valor_individual": 200,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos/{bem_produzido_1.uuid}/', data=json.dumps(payload),
                                                  content_type='application/json')
    content = json.loads(response.content)

    assert content['uuid']
    assert content['associacao']
    assert content['status'] == BemProduzido.STATUS_COMPLETO
    assert response.status_code == status.HTTP_200_OK


def test_post_bem_produzido_com_validacao_rateios(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    associacao_1, despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    rateio_1 = rateio_despesa_factory(associacao=associacao_1, despesa=despesa_2025_1, valor_rateio=200)

    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 7124
            },
        ],
        "itens": [
            {
                "num_processo_incorporacao": 985734857456873,
                "quantidade": 1,
                "valor_individual": 7124,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.post('/api/bens-produzidos/', data=json.dumps(payload),
                                                 content_type='application/json')
    content = json.loads(response.content)

    assert content[
        "mensagem"] == f"O valor utilizado (7124.00) excede o valor disponível (200.00) para o rateio {rateio_1.uuid}."
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_post_bem_produzido_com_validacao_itens(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    associacao_1, despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    rateio_1 = rateio_despesa_factory(associacao=associacao_1, despesa=despesa_2025_1, valor_rateio=500)

    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 500
            },
        ],
        "itens": [
            {
                "num_processo_incorporacao": 985734857456873,
                "quantidade": 1,
                "valor_individual": 7124,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.post('/api/bens-produzidos/', data=json.dumps(payload),
                                                 content_type='application/json')
    content = json.loads(response.content)

    assert content["mensagem"] == 'A soma dos valores dos itens não bate com o valor total disponível.'
    assert content["valor_total_itens"] == '7124.0'
    assert content["valor_total_esperado"] == '500.0'
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_post_bem_produzido_rascunho(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    associacao_1, despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    rateio_1 = rateio_despesa_factory(associacao=associacao_1, despesa=despesa_2025_1, valor_rateio=200)

    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [
            {
                "uuid": f"{rateio_1.uuid}",
                "valor_utilizado": 200
            },
        ],
        "itens": [
            {
                "num_processo_incorporacao": 985734857456873,
                "quantidade": 1,
                "valor_individual": 200,
                "especificacao_do_bem": f"{especificacao_material_servico_1.uuid}"
            }
        ],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.post('/api/bens-produzidos-rascunho/', data=json.dumps(payload),
                                                 content_type='application/json')
    content = json.loads(response.content)

    assert content['uuid']
    assert content['associacao']
    assert content['status'] == BemProduzido.STATUS_INCOMPLETO
    assert response.status_code == status.HTTP_201_CREATED


def test_post_bem_produzido_rascunho_campos_vazios(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    associacao_1, despesa_factory,
):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')

    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [],
        "itens": [],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.post('/api/bens-produzidos-rascunho/', data=json.dumps(payload),
                                                 content_type='application/json')
    content = json.loads(response.content)

    assert content['uuid']
    assert content['associacao']
    assert content['status'] == BemProduzido.STATUS_INCOMPLETO
    assert response.status_code == status.HTTP_201_CREATED


def test_patch_bem_produzido_rascunho(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    bem_produzido_1,
    associacao_1, despesa_factory,
):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')

    payload = {
        "despesas": [f"{despesa_2025_1.uuid}"],
        "rateios": [],
        "itens": [],
        "associacao": f"{associacao_1.uuid}"
    }

    response = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos-rascunho/{bem_produzido_1.uuid}/', data=json.dumps(payload),
                                                  content_type='application/json')
    content = json.loads(response.content)

    assert content['uuid']
    assert content['associacao']
    assert content['status'] == BemProduzido.STATUS_INCOMPLETO
    assert response.status_code == status.HTTP_200_OK


def test_excluir_em_lote_despesas_do_bem_produzido(
        jwt_authenticated_client_sme,
        flag_situacao_patrimonial,
        bem_produzido_2,
        bem_produzido_despesa_2,
        bem_produzido_despesa_3,
        bem_produzido_despesa_4
):
    """Testa a exclusão em lote de despesas associadas a um bem produzido."""
    payload = {
        "uuids": [
            str(bem_produzido_despesa_2.despesa.uuid),
            str(bem_produzido_despesa_3.despesa.uuid),
        ]
    }

    assert bem_produzido_2.despesas.count(
    ) == 3, f"Esperado 3 despesa associada ao bem produzido, obtido {bem_produzido_2.despesas.count()}"

    response = jwt_authenticated_client_sme.post(
        f'/api/bens-produzidos/{bem_produzido_2.uuid}/excluir-lote/', content_type='application/json', data=json.dumps(payload))

    assert response.status_code == status.HTTP_200_OK, response.content

    assert bem_produzido_2.despesas.count(
    ) == 1, f"Esperado 1 despesa associada ao bem produzido, obtido {bem_produzido_2.despesas.count()}"


def test_excluir_em_lote_payload_invalido(
        jwt_authenticated_client_sme,
        flag_situacao_patrimonial,
        bem_produzido_2,
):
    response = jwt_authenticated_client_sme.post(
        f'/api/bens-produzidos/{bem_produzido_2.uuid}/excluir-lote/', content_type='application/json', data=json.dumps({"uuids": "nao_lista"}))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
