import json
from datetime import date

import pytest
from rest_framework import status
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def conta_associacao_teste_solicitar_envio_do_comprovante_do_saldo_da_conta(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def periodo_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta():
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
    )


@pytest.fixture
def prestacao_conta_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta(
    periodo_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta,
        associacao=associacao,
        status=PrestacaoConta.STATUS_EM_ANALISE
    )


@pytest.fixture
def analise_prestacao_conta_teste_solicitar_envio_do_comprovante_do_saldo_da_conta(
    prestacao_conta_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta,
    )


def test_salvar_ajustes_saldo_conta(
    analise_prestacao_conta_teste_solicitar_envio_do_comprovante_do_saldo_da_conta,
    prestacao_conta_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta,
    periodo_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta,
    conta_associacao_teste_solicitar_envio_do_comprovante_do_saldo_da_conta,
    jwt_authenticated_client_a
):
    payload = {
        'analise_prestacao_conta': f'{analise_prestacao_conta_teste_solicitar_envio_do_comprovante_do_saldo_da_conta.uuid}',
        'conta_associacao': f'{conta_associacao_teste_solicitar_envio_do_comprovante_do_saldo_da_conta.uuid}',
        'prestacao_conta': f'{prestacao_conta_2020_1_teste_solicitar_envio_do_comprovante_do_saldo_da_conta.uuid}',
        'data_extrato': "2023-07-04",
        'saldo_extrato': 100,
        'solicitar_envio_do_comprovante_do_saldo_da_conta': True,
        'observacao_solicitar_envio_do_comprovante_do_saldo_da_conta': 'Observação do Teste Action Salvar Ajustes Saldo Conta ',
    }

    response = jwt_authenticated_client_a.post(
        '/api/analises-conta-prestacao-conta/salvar-ajustes-saldo-conta/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
