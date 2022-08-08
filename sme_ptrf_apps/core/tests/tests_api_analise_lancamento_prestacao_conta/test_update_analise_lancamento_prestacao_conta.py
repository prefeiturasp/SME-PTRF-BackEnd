import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import AnaliseLancamentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_update_analise_lancamento(
    jwt_authenticated_client_a,
    analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa
):
    analise = AnaliseLancamentoPrestacaoConta.objects.get(
        uuid=analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa.uuid)

    assert analise.justificativa == "teste"

    payload = {
        'justificativa': 'Teste update funcionando',
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/analises-lancamento-prestacao-conta/{analise.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    analise_update = AnaliseLancamentoPrestacaoConta.objects.get(
        uuid=analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert analise_update.justificativa == payload['justificativa']
