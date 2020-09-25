import json
import pytest

from datetime import date

from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_recebe_prestacao_conta(client, prestacao_conta):
    payload = {
        'data_recebimento': '2020-10-01',
    }

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/receber/'

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_RECEBIDA, 'Status não atualizado para RECEBIDA.'
    assert prestacao_atualizada.data_recebimento == date(2020, 10, 1), 'Data de recebimento não atualizada.'
