import pytest
from datetime import datetime
from freezegun import freeze_time
from rest_framework import status
from sme_ptrf_apps.paa.models import Paa

pytestmark = pytest.mark.django_db


@freeze_time('2025-01-01')
def test_desativar_atualizacao_saldo(jwt_authenticated_client_sme, periodo_paa_2025_1, flag_paa, paa_factory, acao_associacao_factory):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_2025_1,
    )

    acao_associacao_factory.create(associacao=paa.associacao)
    acao_associacao_factory.create(associacao=paa.associacao)

    response = jwt_authenticated_client_sme.post(f"/api/paa/{paa.uuid}/desativar-atualizacao-saldo/")

    result = response.json()
    paa = Paa.objects.get(id=paa.id)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2
    assert paa.saldo_congelado_em == datetime(2025, 1, 1, 0, 0)


def test_ativar_atualizacao_saldo(jwt_authenticated_client_sme, periodo_paa_2025_1, flag_paa, paa_factory, acao_associacao_factory):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_2025_1,
    )

    acao_associacao_factory.create(associacao=paa.associacao)
    acao_associacao_factory.create(associacao=paa.associacao)

    response = jwt_authenticated_client_sme.post(f"/api/paa/{paa.uuid}/ativar-atualizacao-saldo/")

    result = response.json()
    paa = Paa.objects.get(id=paa.id)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2
    assert paa.saldo_congelado_em is None
