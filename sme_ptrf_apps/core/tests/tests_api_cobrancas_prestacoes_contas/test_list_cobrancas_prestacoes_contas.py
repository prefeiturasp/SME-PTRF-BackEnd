import json
from datetime import date

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def _cobranca_prestacao_2020_1_recebimento(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'CobrancaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo='RECEBIMENTO',
        data=date(2020, 7, 1),
    )


@pytest.fixture
def _devolucao_prestacao_conta_2020_1_dev_1(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
    )

@pytest.fixture
def _cobranca_prestacao_2020_1_devolucao(prestacao_conta_2020_1_conciliada, _devolucao_prestacao_conta_2020_1_dev_1):
    return baker.make(
        'CobrancaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo='DEVOLUCAO',
        data=date(2020, 7, 1),
        devolucao_prestacao=_devolucao_prestacao_conta_2020_1_dev_1
    )


@pytest.fixture
def _devolucao_prestacao_conta_2020_1_dev_2(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        data=date(2020, 7, 11),
        data_limite_ue=date(2020, 8, 11),
    )

@pytest.fixture
def _cobranca_prestacao_2020_1_devolucao_2(prestacao_conta_2020_1_conciliada, _devolucao_prestacao_conta_2020_1_dev_2):
    return baker.make(
        'CobrancaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo='DEVOLUCAO',
        data=date(2020, 7, 12),
        devolucao_prestacao=_devolucao_prestacao_conta_2020_1_dev_2
    )

@pytest.fixture
def _cobranca_prestacao_2019_2_recebimento(prestacao_conta_2019_2_conciliada):
    return baker.make(
        'CobrancaPrestacaoConta',
        prestacao_conta=prestacao_conta_2019_2_conciliada,
        tipo='RECEBIMENTO',
        data=date(2020, 7, 1),
    )


@pytest.fixture
def _cobranca_prestacao_2019_2_devolucao(prestacao_conta_2019_2_conciliada):
    return baker.make(
        'CobrancaPrestacaoConta',
        prestacao_conta=prestacao_conta_2019_2_conciliada,
        tipo='DEVOLUCAO',
        data=date(2020, 7, 1),
    )


def test_list_cobrancas_prestacoes_contas_recebimento(jwt_authenticated_client_a,
                                                      _cobranca_prestacao_2020_1_devolucao,
                                                      _cobranca_prestacao_2020_1_recebimento,
                                                      _cobranca_prestacao_2019_2_devolucao,
                                                      _cobranca_prestacao_2019_2_recebimento):
    prestacao_uuid = _cobranca_prestacao_2020_1_recebimento.prestacao_conta.uuid

    response = jwt_authenticated_client_a.get(f'/api/cobrancas-prestacoes-contas/?prestacao_conta__uuid={prestacao_uuid}&tipo=RECEBIMENTO',
                          content_type='application/json')

    result = json.loads(response.content)

    esperado = [
        {
            'uuid': f'{_cobranca_prestacao_2020_1_recebimento.uuid}',
            'prestacao_conta': f'{_cobranca_prestacao_2020_1_recebimento.prestacao_conta.uuid}',
            'data': '2020-07-01',
            'tipo': 'RECEBIMENTO',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_list_cobrancas_prestacoes_contas_por_devolucao(jwt_authenticated_client_a,
                                                        _cobranca_prestacao_2020_1_devolucao,
                                                        _cobranca_prestacao_2020_1_recebimento,
                                                        _cobranca_prestacao_2019_2_devolucao,
                                                        _cobranca_prestacao_2019_2_recebimento,
                                                        _cobranca_prestacao_2020_1_devolucao_2):

    prestacao_uuid = _cobranca_prestacao_2020_1_recebimento.prestacao_conta.uuid

    devolucao_uuid = _cobranca_prestacao_2020_1_devolucao_2.devolucao_prestacao.uuid

    response = jwt_authenticated_client_a.get(f'/api/cobrancas-prestacoes-contas/?prestacao_conta__uuid={prestacao_uuid}&tipo=DEVOLUCAO&devolucao_prestacao__uuid={devolucao_uuid}',
                          content_type='application/json')

    result = json.loads(response.content)

    esperado = [
        {
            'uuid': f'{_cobranca_prestacao_2020_1_devolucao_2.uuid}',
            'prestacao_conta': f'{_cobranca_prestacao_2020_1_devolucao_2.prestacao_conta.uuid}',
            'data': '2020-07-12',
            'tipo': 'DEVOLUCAO',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
