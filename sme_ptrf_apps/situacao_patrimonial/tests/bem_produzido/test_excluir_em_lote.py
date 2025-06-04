from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json
import pytest

from rest_framework import status

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

pytestmark = pytest.mark.django_db

def test_excluir_em_lote_despesas_do_bem_produzido(jwt_authenticated_client_sme, flag_situacao_patrimonial, bem_produzido_2, bem_produzido_despesa_2, bem_produzido_despesa_3, bem_produzido_despesa_4):
  """Testa a exclusão em lote de despesas associadas a um bem produzido."""
  payload = {
    "uuids": [
      str(bem_produzido_despesa_2.uuid),
      str(bem_produzido_despesa_3.uuid),
    ]
  }

  assert bem_produzido_2.despesas.count() == 3, f"Esperado 3 despesa associada ao bem produzido, obtido {bem_produzido_2.despesas.count()}"
  
  response = jwt_authenticated_client_sme.post(f'/api/bens-produzidos/{bem_produzido_2.uuid}/excluir-lote/', content_type='application/json', data=json.dumps(payload))
  
  print(response.content)
  
  assert response.status_code == status.HTTP_200_OK, response.content

  assert bem_produzido_2.despesas.count() == 1, f"Esperado 1 despesa associada ao bem produzido, obtido {bem_produzido_2.despesas.count()}"
