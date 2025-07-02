import json
import pytest

from rest_framework import status

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

pytestmark = pytest.mark.django_db

def test_alterar_status_cadastrar_bem_produzido(jwt_authenticated_client_sme, flag_situacao_patrimonial, despesa_factory, associacao_factory, rateio_despesa_factory, bem_produzido_factory, bem_produzido_despesa_factory, bem_produzido_rateio_factory, especificacao_material_servico_factory, bem_produzido_item_factory):
  
  associacao = associacao_factory.create()
  esp_mat_serv = especificacao_material_servico_factory.create()
  bem_produzido = bem_produzido_factory.create(associacao=associacao)
  
  despesa_1 = despesa_factory.create(associacao=associacao)
  rateio_1_1 = rateio_despesa_factory.create(associacao=associacao, despesa=despesa_1, valor_rateio=200.0)
  rateio_1_2 = rateio_despesa_factory.create(associacao=associacao, despesa=despesa_1, valor_rateio=300.0)
  bem_produzido_despesa_1 = bem_produzido_despesa_factory.create(bem_produzido=bem_produzido, despesa=despesa_1)
  bem_produzido_rateio_1_1 = bem_produzido_rateio_factory.create(bem_produzido_despesa=bem_produzido_despesa_1, rateio=rateio_1_1, valor_utilizado=130.0)
  bem_produzido_rateio_1_2 = bem_produzido_rateio_factory.create(bem_produzido_despesa=bem_produzido_despesa_1, rateio=rateio_1_2, valor_utilizado=20.0)
  
  despesa_2 = despesa_factory.create(associacao=associacao)
  rateio_2_1 = rateio_despesa_factory.create(associacao=associacao, despesa=despesa_2, valor_rateio=200.0)
  bem_produzido_despesa_2 = bem_produzido_despesa_factory.create(bem_produzido=bem_produzido, despesa=despesa_2)
  bem_produzido_rateio_2_1 = bem_produzido_rateio_factory.create(bem_produzido_despesa=bem_produzido_despesa_2, rateio=rateio_2_1, valor_utilizado=10.0)
  
  bem_produzido_item_1 = bem_produzido_item_factory.create(
    bem_produzido=bem_produzido,
    especificacao_do_bem=esp_mat_serv,
    num_processo_incorporacao="123456789012345",
    quantidade=1,
    valor_individual=100.0
  )
  
  """Testa falha ao tentar cadastar bem com total de valores dos rateios incompletos."""
  assert bem_produzido.status == BemProduzido.STATUS_INCOMPLETO

  payload_1 = {
    "itens": [
      {
        "num_processo_incorporacao": "222222222222222",
        "quantidade": 1,
        "valor_individual": "10.00",
        "especificacao_do_bem": str(esp_mat_serv.uuid)
      },
      {
        "uuid": str(bem_produzido_item_1.uuid),
        "num_processo_incorporacao": "11111111111111",
        "quantidade": 2,
        "valor_individual": "80.00",
        "especificacao_do_bem": str(esp_mat_serv.uuid)
      }
    ]
  }
  
  response = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos/{bem_produzido.uuid}/cadastrar-bem/', content_type='application/json', data=json.dumps(payload_1))
  
  bem_produzido.refresh_from_db()
  
  assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
  assert bem_produzido.status == BemProduzido.STATUS_INCOMPLETO, f"A soma dos valores dos itens não bate com o valor total disponível. valor_total_itens: 170.0, valor_total_esperado: 160.0"
  
  """Testa ação de alterar o status ao cadastrar um bem produzido."""
  payload_2 = {
    "itens": [
      {
        "num_processo_incorporacao": "222222222222222",
        "quantidade": 1,
        "valor_individual": "10.00",
        "especificacao_do_bem": str(esp_mat_serv.uuid)
      },
      {
        "uuid": str(bem_produzido_item_1.uuid),
        "num_processo_incorporacao": "11111111111111",
        "quantidade": 2,
        "valor_individual": "75.00",
        "especificacao_do_bem": str(esp_mat_serv.uuid)
      }
    ]
  }
  
  response = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos/{bem_produzido.uuid}/cadastrar-bem/', content_type='application/json', data=json.dumps(payload_2))
  
  bem_produzido.refresh_from_db()
  
  """Testa ação de alterar o status ao cadastrar um bem produzido."""
  assert response.status_code == status.HTTP_201_CREATED, response.content
  assert bem_produzido.status == BemProduzido.STATUS_COMPLETO, f"Esperado o status COMPLETO do bem produzido, obtido {bem_produzido.status}"