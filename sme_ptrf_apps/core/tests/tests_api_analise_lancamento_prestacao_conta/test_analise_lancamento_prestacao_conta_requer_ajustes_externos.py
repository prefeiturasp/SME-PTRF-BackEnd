import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import AnaliseLancamentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_analise_lancamento_requer_ajustes_externos(
    jwt_authenticated_client_a,
    analise_lancamento_receita_requer_ajustes_externos,
    tipo_acerto_requer_ajuste_externo,
    solicitacao_acerto_requer_ajuste_externo,
):
    analise = AnaliseLancamentoPrestacaoConta.objects.get(
        uuid=analise_lancamento_receita_requer_ajustes_externos.uuid)

    response = jwt_authenticated_client_a.get(
        f'/api/analises-lancamento-prestacao-conta/{analise.uuid}/',
        content_type='applicaton/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert analise.requer_ajustes_externos


def test_analise_lancamento_requer_ajustes_externos_sem_solicitacao_de_acertos(
    jwt_authenticated_client_a,
    analise_lancamento_receita_requer_ajustes_externos,
    tipo_acerto_requer_ajuste_externo,
):
    analise = AnaliseLancamentoPrestacaoConta.objects.get(
        uuid=analise_lancamento_receita_requer_ajustes_externos.uuid)

    response = jwt_authenticated_client_a.get(
        f'/api/analises-lancamento-prestacao-conta/{analise.uuid}/',
        content_type='applicaton/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert not analise.requer_ajustes_externos
