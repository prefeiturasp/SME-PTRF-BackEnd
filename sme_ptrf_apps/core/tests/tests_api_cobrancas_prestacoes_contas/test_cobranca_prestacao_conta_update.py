import json
import pytest
from datetime import date
from rest_framework import status

from sme_ptrf_apps.core.models import CobrancaPrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_troca_data_cobranca(cobranca_prestacao_devolucao):
    payload = {
        'data': '2020-01-01',
    }
    return payload


def test_update_processo_associacao(jwt_authenticated_client_a, cobranca_prestacao_devolucao, payload_troca_data_cobranca):

    assert CobrancaPrestacaoConta.objects.filter(uuid=cobranca_prestacao_devolucao.uuid).exists()

    cobranca_anterior = CobrancaPrestacaoConta.objects.filter(uuid=cobranca_prestacao_devolucao.uuid).get()

    assert cobranca_anterior.data == date(2020, 7, 1), "Não é data inicial esperada"

    response = jwt_authenticated_client_a.patch(
        f'/api/cobrancas-prestacoes-contas/{cobranca_prestacao_devolucao.uuid}/',
        data=json.dumps(payload_troca_data_cobranca),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert CobrancaPrestacaoConta.objects.filter(uuid=result['uuid']).exists()

    cobranca = CobrancaPrestacaoConta.objects.filter(uuid=result['uuid']).get()

    assert cobranca.data == date(2020,1,1), "Data não foi alterada"
