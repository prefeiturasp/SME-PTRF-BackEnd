import json

import pytest
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_reabre_prestacao_conta(client, prestacao_conta):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/reabrir/'

    response = client.delete(url, content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not PrestacaoConta.objects.filter(uuid=prestacao_conta.uuid).exists(), 'Não apagou a PC'
