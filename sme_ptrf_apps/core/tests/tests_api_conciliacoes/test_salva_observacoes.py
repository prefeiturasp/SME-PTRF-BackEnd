import json

import pytest

from datetime import date

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

from ...models import ObservacaoConciliacao
from ...models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao

pytestmark = pytest.mark.django_db


def test_api_salva_observacoes_conciliacao_justificativa(jwt_authenticated_client_a, periodo, conta_associacao_cartao):
    url = f'/api/conciliacoes/salvar-observacoes/'

    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "observacao": "Teste observações.",
        "justificativa_ou_extrato_bancario": "JUSTIFICATIVA"
    }

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert ObservacaoConciliacao.objects.exists()

    obj = ObservacaoConciliacao.objects.first()
    assert obj.data_extrato is None
    assert obj.saldo_extrato == 0.0
    assert obj.texto == "Teste observações."


def test_api_salva_observacoes_conciliacao_extrato_bancario(jwt_authenticated_client_a, periodo,
                                                            conta_associacao_cartao):
    url = '/api/conciliacoes/salvar-observacoes/'

    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "data_extrato": "2021-01-01",
        "saldo_extrato": 1000.00,
        "justificativa_ou_extrato_bancario": "EXTRATO_BANCARIO"
    }

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert ObservacaoConciliacao.objects.exists()

    obj = ObservacaoConciliacao.objects.first()
    assert obj.data_extrato == periodo.data_fim_realizacao_despesas
    assert obj.saldo_extrato == 1000.0


def test_api_salva_observacoes_extrato_bancario_com_solicitacao_encerramento(
        jwt_authenticated_client_a,
        periodo_2019_1,
        conta_associacao,
        solicitacao_encerramento_conta_associacao_factory):

    solicitacao_encerramento_conta_associacao_factory.create(
        conta_associacao=conta_associacao,
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA,
        data_de_encerramento_na_agencia=date(2019, 5, 1),
    )
    url = "/api/conciliacoes/salvar-observacoes/"
    payload = {
        'periodo_uuid': f'{periodo_2019_1.uuid}',
        'conta_associacao_uuid': f'{conta_associacao.uuid}',
        'data_extrato': '2021-01-01',
        'saldo_extrato': 1000.00,
        'justificativa_ou_extrato_bancario': 'EXTRATO_BANCARIO',
    }

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    obj = ObservacaoConciliacao.objects.get()
    assert obj.data_extrato == date(2019, 5, 1)
    assert obj.saldo_extrato == 1000.0


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
