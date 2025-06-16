import json
import pytest

from rest_framework import status

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

pytestmark = pytest.mark.django_db

def test_patch_bens_produzidos(jwt_authenticated_client_sme, flag_situacao_patrimonial, bem_produzido_1, bem_produzido_despesa_1, bem_produzido_rateio_1, rateio_1):
  """Testa a alteração do valor utilizado do rateio de um bem produzido."""
  assert bem_produzido_rateio_1.valor_utilizado == 120.00
  
  payload = {
    "rateios":[
      {
        "uuid": str(rateio_1.uuid),
        "valor_utilizado": 60.00,
        "bem_produzido_despesa": str(bem_produzido_despesa_1.uuid),
      }
  ]}
  
  response = jwt_authenticated_client_sme.patch(f'/api/bens-produzidos/{bem_produzido_1.uuid}/',content_type='application/json',data=json.dumps(payload))
  
  assert response.status_code == status.HTTP_200_OK, response.content
  
  bem_produzido_rateio_1.refresh_from_db()

  assert bem_produzido_rateio_1.valor_utilizado == 60.00, f"Esperado o valor de 60.00 no rateio do bem produzido e obteve {bem_produzido_rateio_1.valor_utilizado}"