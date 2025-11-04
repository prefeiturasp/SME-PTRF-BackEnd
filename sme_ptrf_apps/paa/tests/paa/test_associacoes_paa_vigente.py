import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


@freeze_time('2025-04-1 10:11:12')
def test_get_paa_vigente(jwt_authenticated_client_sme, paa):
    response = jwt_authenticated_client_sme.get(f'/api/associacoes/{paa.associacao.uuid}/paa-vigente/')

    assert response.status_code == status.HTTP_200_OK


def test_get_sem_paa_vigente(jwt_authenticated_client_sme, associacao_cadastro_incompleto):
    response = jwt_authenticated_client_sme.get(f'/api/associacoes/{associacao_cadastro_incompleto.uuid}/paa-vigente/')

    assert response.status_code == status.HTTP_404_NOT_FOUND
