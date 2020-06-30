import json

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from sme_ptrf_apps.core.models import ContaAssociacao

from ...api.views.associacoes_viewset import AssociacoesViewSet

pytestmark = pytest.mark.django_db


def test_view_set(associacao, fake_user):
    request = APIRequestFactory().get("")
    detalhe = AssociacoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=associacao.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_get_contas_associacoes(jwt_authenticated_client, associacao, conta_associacao, conta_associacao_cartao, conta_associacao_cheque):
    response = jwt_authenticated_client.get(
        f'/api/associacoes/{associacao.uuid}/contas/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert str(conta_associacao_cartao.uuid) in [c['uuid'] for c in result]
    assert str(conta_associacao_cheque.uuid) in [c['uuid'] for c in result]


def test_update_contas_associacoes(jwt_authenticated_client, associacao, tipo_conta_cartao, tipo_conta_cheque, conta_associacao, conta_associacao_cartao, conta_associacao_cheque):
    payload =  [
        {
            "uuid": str(conta_associacao_cartao.uuid),
            "tipo_conta": tipo_conta_cartao.id,
            "banco_nome": "Banco Inter",
            "agencia": "7777-3",
            "numero_conta": "4444-7"
        },
        {
            "uuid": str(conta_associacao_cheque.uuid),
            "tipo_conta": tipo_conta_cheque.id,
            "banco_nome": "Banco Santander",
            "agencia": "9812-8",
            "numero_conta": "00934-2"
        }
    ]

    response = jwt_authenticated_client.post(
        f'/api/associacoes/{associacao.uuid}/contas-update/', data=json.dumps(payload), content_type='application/json')

    conta_cartao = ContaAssociacao.objects.filter(uuid=conta_associacao_cartao.uuid).get()
    conta_cheque = ContaAssociacao.objects.filter(uuid=conta_associacao_cheque.uuid).get()

    assert response.status_code == status.HTTP_200_OK

    assert conta_cartao.banco_nome == "Banco Inter"
    assert conta_cartao.agencia == "7777-3"
    assert conta_cartao.numero_conta == "4444-7"

    assert conta_cheque.banco_nome == "Banco Santander"
    assert conta_cheque.agencia == "9812-8"
    assert conta_cheque.numero_conta == "00934-2"
