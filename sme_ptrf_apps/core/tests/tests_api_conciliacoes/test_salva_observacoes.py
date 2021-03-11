import json

import pytest

from datetime import date

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

from ...models import ObservacaoConciliacao

pytestmark = pytest.mark.django_db


def test_api_salva_observacoes_conciliacao(jwt_authenticated_client_a, periodo, conta_associacao_cartao):
    url = f'/api/conciliacoes/salvar-observacoes/'

    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "observacao": "Teste observações.",
        "data_extrato": "2021-01-01",
        "saldo_extrato": 1000.00,
    }

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert ObservacaoConciliacao.objects.exists()

    obj = ObservacaoConciliacao.objects.first()
    assert obj.data_extrato == date(2021, 1, 1)
    assert obj.saldo_extrato == 1000.0
    assert obj.texto == "Teste observações."


def test_api_salva_observacoes_conciliacao_vazia(jwt_authenticated_client_a, periodo,
                                                 conta_associacao_cartao):
    url = f'/api/conciliacoes/salvar-observacoes/'

    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "observacao": "",
        "data_extrato": "",
        "saldo_extrato": 0,
    }

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert not ObservacaoConciliacao.objects.exists()
