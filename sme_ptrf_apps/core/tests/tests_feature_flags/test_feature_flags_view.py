import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_feature_flags_sem_flags_cadastradas(client):
    response = client.get('/api/feature-flags')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {}


def test_feature_flags_retorna_flags(client, flag_factory):
    flag_ativa = flag_factory(name='flag-ativa-teste', everyone=True)
    flag_inativa = flag_factory(name='flag-inativa-teste', everyone=False)

    response = client.get('/api/feature-flags')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result[flag_ativa.name] is True
    assert result[flag_inativa.name] is False
