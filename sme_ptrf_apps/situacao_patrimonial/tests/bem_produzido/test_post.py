from datetime import date
import json
import pytest

from rest_framework import status

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

pytestmark = pytest.mark.django_db

def test_create(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_factory, despesa_factory):
  associacao = associacao_factory.create()
  despesa_1 = despesa_factory.create(
        data_transacao=date(2023, 1, 1),
        valor_total=50,
        associacao=associacao
    )
  despesa_2 = despesa_factory.create(
        data_transacao=date(2023, 4, 4),
        valor_total=100,
        associacao=associacao
    )
  payload = {
    "associacao": str(associacao.uuid),
    "despesas": [
      str(despesa_1.uuid),
      str(despesa_2.uuid)
    ]
  }
  
  response = jwt_authenticated_client_sme.post('/api/bens-produzidos/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))
  
  assert response.status_code == status.HTTP_201_CREATED, response.content
  bem_produzido = BemProduzido.objects.all()
  assert len(bem_produzido) == 1