import json

import pytest
from rest_framework import status

from ...api.serializers import AtaLookUpSerializer

pytestmark = pytest.mark.django_db


def test_api_inicia_ata_nao_existente(client,
                                      prestacao_conta_iniciada,
                                      ):
    prestacao_uuid = prestacao_conta_iniciada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/iniciar-ata/'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = AtaLookUpSerializer(prestacao_conta_iniciada.ultima_ata(), many=False).data

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a ata esperada."


def test_api_inicia_ata_ja_existente(client,
                                     prestacao_conta_iniciada,
                                     ata_prestacao_conta_iniciada
                                     ):
    prestacao_uuid = prestacao_conta_iniciada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/iniciar-ata/'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'ata-ja-iniciada',
        'mensagem': 'Já existe uma ata iniciada para essa prestação de contas.'
    }

    assert response.status_code == status.HTTP_409_CONFLICT
    assert result == result_esperado, "Deveria ter retornado erro ata já iniciada."
