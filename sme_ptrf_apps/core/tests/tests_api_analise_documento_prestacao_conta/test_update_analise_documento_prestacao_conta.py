import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import AnaliseDocumentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_update_analise_documento(
    jwt_authenticated_client_a,
    analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta
):
    analise = AnaliseDocumentoPrestacaoConta.objects.get(
        uuid=analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta.uuid)

    assert analise.justificativa == "TESTE"

    payload = {
        'justificativa': 'Teste update funcionando',
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/analises-documento-prestacao-conta/{analise.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    analise_update = AnaliseDocumentoPrestacaoConta.objects.get(
        uuid=analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert analise_update.justificativa == payload['justificativa']
