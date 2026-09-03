import pytest
from datetime import datetime
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_resumo_prioridades_com_saldo_congelado(jwt_authenticated_client_sme, flag_paa, paa_factory):

    paa = paa_factory.create(saldo_congelado_em=datetime(2026, 9, 3))

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(paa.uuid)}/resumo-prioridades/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result[0]['key'] == 'PTRF'
    assert result[0]['saldo_congelado_em'] == '03/09/2026'


def test_resumo_prioridades_sem_saldo_congelado(jwt_authenticated_client_sme, flag_paa, paa_factory):

    paa = paa_factory.create(saldo_congelado_em=None)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(paa.uuid)}/resumo-prioridades/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result[0]['key'] == 'PTRF'
    assert result[0]['saldo_congelado_em'] == ''
