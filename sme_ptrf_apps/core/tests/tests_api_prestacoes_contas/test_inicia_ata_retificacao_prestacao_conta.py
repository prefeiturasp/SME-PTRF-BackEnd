import json

import pytest
from rest_framework import status

from ...api.serializers import AtaLookUpSerializer

pytestmark = pytest.mark.django_db


def test_api_inicia_ata_retificacao_nao_existente(jwt_authenticated_client_a,
                                                  prestacao_conta_iniciada,
                                                  ):
    prestacao_uuid = prestacao_conta_iniciada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/iniciar-ata-retificacao/'

    response = jwt_authenticated_client_a.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = AtaLookUpSerializer(prestacao_conta_iniciada.ultima_ata_retificacao(), many=False).data

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a ata esperada."


def test_api_inicia_ata_retificacao_ja_existente(jwt_authenticated_client_a,
                                                 prestacao_conta_iniciada,
                                                 ata_prestacao_conta_iniciada,
                                                 ata_retificacao_prestacao_conta_iniciada,
                                                 ):
    prestacao_uuid = prestacao_conta_iniciada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/iniciar-ata-retificacao/'

    response = jwt_authenticated_client_a.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'ata-ja-iniciada',
        'mensagem': 'Já existe uma ata de retificação iniciada para essa prestação de contas.'
    }

    assert response.status_code == status.HTTP_409_CONFLICT
    assert result == result_esperado, "Deveria ter retornado erro ata já iniciada."
