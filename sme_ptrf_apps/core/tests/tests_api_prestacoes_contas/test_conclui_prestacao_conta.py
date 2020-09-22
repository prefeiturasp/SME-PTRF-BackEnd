import json

import pytest
from django.db.models import Q
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_conclui_prestacao_conta(client, associacao, periodo):
    associacao_uuid = associacao.uuid
    periodo_uuid = periodo.uuid

    url = f'/api/prestacoes-contas/concluir/?associacao_uuid={associacao_uuid}&periodo_uuid={periodo_uuid}'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = PrestacaoContaLookUpSerializer(
        PrestacaoConta.objects.get(Q(associacao__uuid=associacao_uuid), Q(periodo__uuid=periodo_uuid)),
        many=False).data

    # Converto os campos UUIDs em strings para que a comparação funcione
    result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a prestação de contas esperada."

def test_api_conclui_prestacao_conta_sem_periodo(client, periodo, associacao):
    associacao_uuid = associacao.uuid

    url = f'/api/prestacoes-contas/concluir/?associacao_uuid={associacao_uuid}'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o uuid do período de conciliação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado


def test_api_conclui_prestacao_conta_sem_associacao(client, periodo, associacao):
    periodo_uuid = periodo.uuid

    url = f'/api/prestacoes-contas/concluir/?periodo_uuid={periodo_uuid}'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o uuid da associação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado

def test_api_conclui_prestacao_conta_ja_existente(client, prestacao_conta):
    associacao_uuid = prestacao_conta.associacao.uuid
    periodo_uuid = prestacao_conta.periodo.uuid

    url = f'/api/prestacoes-contas/concluir/?associacao_uuid={associacao_uuid}&periodo_uuid={periodo_uuid}'


    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'prestacao_ja_iniciada',
        'mensagem': 'Você não pode iniciar uma prestação de contas que já foi iniciada.'
    }

    assert response.status_code == status.HTTP_409_CONFLICT
    assert result == result_esperado
