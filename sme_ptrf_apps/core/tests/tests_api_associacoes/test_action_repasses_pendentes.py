import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_repasses_pendentes_por_periodo(jwt_authenticated_client_a, associacao, periodo, repasse):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/repasses-pendentes-por-periodo/?periodo_uuid={periodo.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_action_repasses_pendentes_por_periodo_sem_passar_periodo(jwt_authenticated_client_a, associacao, periodo, repasse):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/repasses-pendentes-por-periodo/',
        content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

