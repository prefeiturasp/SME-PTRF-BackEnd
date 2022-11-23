import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import AnaliseDocumentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_retrieve_analise_documento(
    jwt_authenticated_client_a,
    analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta
):
    analise = AnaliseDocumentoPrestacaoConta.objects.get(
        uuid=analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta.uuid)

    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/{analise.uuid}/',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'justificativa': analise.justificativa
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
