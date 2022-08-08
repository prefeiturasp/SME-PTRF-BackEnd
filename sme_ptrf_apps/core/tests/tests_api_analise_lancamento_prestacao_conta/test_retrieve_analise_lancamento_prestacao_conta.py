import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import AnaliseLancamentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_retrieve_analise_lancamento(
    jwt_authenticated_client_a,
    analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa
):
    analise = AnaliseLancamentoPrestacaoConta.objects.get(
        uuid=analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa.uuid)

    response = jwt_authenticated_client_a.get(
        f'/api/analises-lancamento-prestacao-conta/{analise.uuid}/',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'justificativa': analise.justificativa
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

