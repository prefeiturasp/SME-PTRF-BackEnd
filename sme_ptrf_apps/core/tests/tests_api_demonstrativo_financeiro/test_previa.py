import pytest
from unittest.mock import patch
from rest_framework import status

pytestmark = pytest.mark.django_db

URL = '/api/demonstrativo-financeiro/previa/'


def test_previa_retorna_200_e_enfileira_task(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    with patch(
        'sme_ptrf_apps.core.api.views.demonstrativo_financeiro_viewset.gerar_previa_demonstrativo_financeiro_async.delay'  # noqa
    ) as mock_delay:
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'conta-associacao': str(conta_associacao.uuid),
                'periodo': str(periodo.uuid),
                'data_inicio': '2024-01-01',
                'data_fim': '2024-03-31',
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'mensagem': 'Arquivo na fila para processamento.'}
    mock_delay.assert_called_once_with(
        periodo_uuid=str(periodo.uuid),
        conta_associacao_uuid=str(conta_associacao.uuid),
        data_inicio='2024-01-01',
        data_fim='2024-03-31',
        usuario=jwt_authenticated_client_a.handler._force_user.username,
    )


def test_previa_sem_conta_associacao_retorna_400(
    jwt_authenticated_client_a,
    periodo,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'periodo': str(periodo.uuid),
            'data_inicio': '2024-01-01',
            'data_fim': '2024-03-31',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_previa_sem_periodo_retorna_400(
    jwt_authenticated_client_a,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'data_inicio': '2024-01-01',
            'data_fim': '2024-03-31',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_previa_sem_datas_retorna_400(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_previa_data_fim_menor_que_data_inicio_retorna_400(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
            'data_inicio': '2024-03-31',
            'data_fim': '2024-01-01',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'erro_nas_datas'
    assert 'Data fim não pode ser menor que a data inicio.' in response.data['mensagem']


def test_previa_data_fim_maior_que_data_fim_periodo_retorna_400(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
            'data_inicio': '2024-01-01',
            'data_fim': '2024-12-31',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'erro_nas_datas'
    assert 'Data fim não pode ser maior' in response.data['mensagem']


def test_previa_com_periodo_aberto_aceita_qualquer_data_fim(
    jwt_authenticated_client_a,
    periodo_aberto,
    conta_associacao,
):
    with patch(
        'sme_ptrf_apps.core.api.views.demonstrativo_financeiro_viewset.gerar_previa_demonstrativo_financeiro_async.delay'  # noqa
    ):
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'conta-associacao': str(conta_associacao.uuid),
                'periodo': str(periodo_aberto.uuid),
                'data_inicio': '2024-04-01',
                'data_fim': '2025-12-31',
            },
        )

    assert response.status_code == status.HTTP_200_OK
