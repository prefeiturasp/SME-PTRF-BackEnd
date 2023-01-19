import json

import pytest
from datetime import date
from rest_framework import status

from model_bakery import baker

from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_1_test_acion_contas_com_acertos_em_lancamentos():
    return baker.make('Unidade', codigo_eol='00001', tipo_unidade='DRE', nome='DRE 1')


@pytest.fixture
def ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos(dre_1_test_acion_contas_com_acertos_em_lancamentos):
    return baker.make(
        'Unidade',
        codigo_eol='00011',
        dre=dre_1_test_acion_contas_com_acertos_em_lancamentos,
        tipo_unidade='CEU',
        nome='Escola Vassouras'
    )


@pytest.fixture
def associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos(
    ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos,
    periodo_anterior
):
    return baker.make(
        'Associacao',
        nome='Associacao Valença',
        cnpj='52.302.275/0001-83',
        unidade=ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos,
    )


@pytest.fixture
def prestacao_conta_2020_1_conciliada(periodo_2020_1, associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )

@pytest.fixture
def devolucao_prestacao_conta_2020_1(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
        data_retorno_ue=None
    )


@pytest.fixture
def analise_prestacao_conta_2020_1(prestacao_conta_2020_1_conciliada, devolucao_prestacao_conta_2020_1):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1
    )


def test_action_contas_com_acertos_em_lancamentos_nao_deve_passar_parametros_requeridos_02(
    jwt_authenticated_client_a,
    associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos,
    analise_prestacao_conta_2020_1,
):
    associacao_uuid = f"{associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos.uuid}"

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/contas-com-acertos-em-lancamentos/?associacao_uuid={associacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o UUID da Associacao e o UUID da Análise da PC.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro


def test_action_contas_com_acertos_em_lancamentos_nao_deve_passar_parametros_requeridos_01(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1,
):
    analise_prestacao_uuid = analise_prestacao_conta_2020_1.uuid

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/contas-com-acertos-em-lancamentos/?analise_prestacao_uuid={analise_prestacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o UUID da Associacao e o UUID da Análise da PC.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro


def test_action_contas_com_acertos_em_lancamentos_nao_deve_passar_analise_prestacao_uuid_inexistente(
    jwt_authenticated_client_a,
    associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos,
    analise_prestacao_conta_2020_1,
):
    associacao_uuid = f"{associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos.uuid}"
    analise_prestacao_uuid = f"{analise_prestacao_conta_2020_1.uuid}XXX"

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/contas-com-acertos-em-lancamentos/?associacao_uuid={associacao_uuid}&analise_prestacao_uuid={analise_prestacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'Objeto não encontrado.',
        'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro

def test_action_contas_com_acertos_em_lancamentos_nao_deve_passar_associacao_uuid_inexistente(
    jwt_authenticated_client_a,
    associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos,
    analise_prestacao_conta_2020_1,
):
    associacao_uuid = f"{associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos.uuid}XXX"
    analise_prestacao_uuid = analise_prestacao_conta_2020_1.uuid

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/contas-com-acertos-em-lancamentos/?associacao_uuid={associacao_uuid}&analise_prestacao_uuid={analise_prestacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {'erro': 'UUID da Associação inválido.'}

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro


def test_action_contas_com_acertos_em_lancamentos(
    jwt_authenticated_client_a,
    associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos,
    analise_prestacao_conta_2020_1,
):
    associacao_uuid = associacao_valenca_ceu_vassouras_dre_1_test_acion_contas_com_acertos_em_lancamentos.uuid
    analise_prestacao_uuid = analise_prestacao_conta_2020_1.uuid

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/contas-com-acertos-em-lancamentos/?associacao_uuid={associacao_uuid}&analise_prestacao_uuid={analise_prestacao_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

