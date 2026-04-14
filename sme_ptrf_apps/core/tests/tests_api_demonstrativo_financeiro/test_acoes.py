import pytest
from unittest.mock import patch
from rest_framework import status

pytestmark = pytest.mark.django_db

URL = '/api/demonstrativo-financeiro/acoes/'

MOCK_INFO_ACOES = [
    {
        'acao_associacao_uuid': 'uuid-acao-1',
        'acao_associacao_nome': 'Ação 1',
        'saldo_reprogramado': 1000,
        'receitas_no_periodo': 500,
        'despesas_no_periodo': 200,
        'despesas_nao_conciliadas_anteriores': 0,
    },
    {
        'acao_associacao_uuid': 'uuid-acao-2',
        'acao_associacao_nome': 'Ação 2',
        'saldo_reprogramado': 0,
        'receitas_no_periodo': 0,
        'despesas_no_periodo': 0,
        'despesas_nao_conciliadas_anteriores': 0,
    },
]


def test_acoes_sem_parametros_retorna_400(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(URL)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_acoes_sem_conta_associacao_retorna_400(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'associacao_uuid': str(conta_associacao.associacao.uuid),
            'periodo_uuid': str(periodo.uuid),
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_acoes_sem_associacao_uuid_retorna_400(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'periodo_uuid': str(periodo.uuid),
            'conta-associacao': str(conta_associacao.uuid),
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_acoes_sem_periodo_uuid_retorna_400(
    jwt_authenticated_client_a,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'associacao_uuid': str(conta_associacao.associacao.uuid),
            'conta-associacao': str(conta_associacao.uuid),
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_acoes_retorna_200_com_acoes_filtradas(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    with patch(
        'sme_ptrf_apps.core.api.views.demonstrativo_financeiro_viewset.info_acoes_associacao_no_periodo',
        return_value=MOCK_INFO_ACOES,
    ):
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'associacao_uuid': str(conta_associacao.associacao.uuid),
                'periodo_uuid': str(periodo.uuid),
                'conta-associacao': str(conta_associacao.uuid),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert 'info_acoes' in response.data
    # Ação 2 é filtrada por não ter saldo, receitas, despesas ou despesas anteriores
    assert len(response.data['info_acoes']) == 1
    assert response.data['info_acoes'][0]['acao_associacao_uuid'] == 'uuid-acao-1'


def test_acoes_filtra_itens_sem_movimentacao(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    info_sem_movimentacao = [
        {
            'acao_associacao_uuid': 'uuid-acao-vazia',
            'acao_associacao_nome': 'Ação Vazia',
            'saldo_reprogramado': 0,
            'receitas_no_periodo': 0,
            'despesas_no_periodo': 0,
            'despesas_nao_conciliadas_anteriores': 0,
        }
    ]

    with patch(
        'sme_ptrf_apps.core.api.views.demonstrativo_financeiro_viewset.info_acoes_associacao_no_periodo',
        return_value=info_sem_movimentacao,
    ):
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'associacao_uuid': str(conta_associacao.associacao.uuid),
                'periodo_uuid': str(periodo.uuid),
                'conta-associacao': str(conta_associacao.uuid),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['info_acoes'] == []
