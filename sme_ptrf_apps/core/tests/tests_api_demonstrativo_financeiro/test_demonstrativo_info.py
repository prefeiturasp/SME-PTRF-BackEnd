import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

URL = '/api/demonstrativo-financeiro/demonstrativo-info/'


def test_demonstrativo_info_sem_demonstrativo_retorna_pendente(
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

    assert response.status_code == status.HTTP_200_OK
    assert response.data == 'Documento pendente de geração'


def test_demonstrativo_info_com_previa_retorna_str_demonstrativo(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_previa,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == str(demonstrativo_financeiro_previa)


def test_demonstrativo_info_com_prestacao_conta_retorna_str_demonstrativo(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    prestacao_conta,
    demonstrativo_financeiro_final,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == str(demonstrativo_financeiro_final)


def test_demonstrativo_info_previa_tem_prioridade_sobre_final(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    prestacao_conta,
    demonstrativo_financeiro_final,
    demonstrativo_financeiro_previa,
):
    """Quando existe prévia sem prestação_conta, ela tem prioridade."""
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == str(demonstrativo_financeiro_previa)
