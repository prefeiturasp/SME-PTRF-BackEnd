import json

import pytest
from rest_framework import status

from ...api.serializers import AtaLookUpSerializer

pytestmark = pytest.mark.django_db


def test_api_get_ata_retificacao_existente(client,
                                           prestacao_conta_iniciada,
                                           ata_retificacao_prestacao_conta_iniciada,
                                           ata_prestacao_conta_iniciada,
                                           ):
    prestacao_uuid = prestacao_conta_iniciada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/ata-retificacao/'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = AtaLookUpSerializer(ata_retificacao_prestacao_conta_iniciada, many=False).data

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a ata esperada."
    assert result['nome'] == 'Ata de Retificação da prestação de contas'

def test_api_get_ata_retificacao_nao_existente(client,
                                               prestacao_conta_iniciada,
                                               ata_prestacao_conta_iniciada,
                                               ):
    prestacao_uuid = prestacao_conta_iniciada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/ata-retificacao/'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'mensagem': 'Ainda não existe uma ata de retificação para essa prestação de contas.'
    }

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result == result_esperado, "Deveria ter retornado erro ata não encontrada."
