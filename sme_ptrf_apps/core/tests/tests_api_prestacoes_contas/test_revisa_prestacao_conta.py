import json

import pytest
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_revisa_prestacao_conta(client, prestacao_conta):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/revisar/'

    motivo_reabertura = "Correção de erros em algumas despesas."
    payload = {
        "motivo": motivo_reabertura
    }

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    prestacao_atualizada = PrestacaoConta.by_uuid(uuid=prestacao_conta.uuid)

    result_esperado = PrestacaoContaLookUpSerializer(
        prestacao_atualizada,
        many=False).data

    # Converto os campos UUIDs em strings para que a comparação funcione
    result_esperado['conta_associacao_uuid'] = f'{result_esperado["conta_associacao_uuid"]}'
    result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a prestação de contas esperada."

    assert not prestacao_atualizada.conciliado, "Flag conciliado deveria ter voltado a ser falso."
    assert prestacao_atualizada.motivo_reabertura == motivo_reabertura, "Não gravou o motivo da reabertura."
    assert prestacao_atualizada.conciliado_em == None, "Não limpou a data da última conciliação."


def test_api_revisa_prestacao_conta_sem_motivo(client, prestacao_conta):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/revisar/'

    payload = {
        "motivo": ""
    }

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'campo_requerido',
        'mensagem': 'É necessário enviar o motivo de revisão da conciliação.'
    }


    assert response.status_code == status.HTTP_400_BAD_REQUEST, "Não recusou um motivo vazio."
    assert result == result_esperado, "Não retornou a mensagem de erro esperada."


def test_api_revisa_prestacao_conta_sem_payload(client, prestacao_conta):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/revisar/'

    response = client.patch(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'campo_requerido',
        'mensagem': 'É necessário enviar o motivo de revisão da conciliação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST, "Não recusou um motivo vazio."
    assert result == result_esperado, "Não retornou a mensagem de erro esperada."
