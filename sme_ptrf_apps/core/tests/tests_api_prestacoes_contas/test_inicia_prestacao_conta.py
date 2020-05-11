import json

import pytest
from django.db.models import Q
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db

def test_api_inicia_prestacao_conta(client, periodo, conta_associacao):
    conta_associacao_uuid = conta_associacao.uuid
    periodo_uuid = periodo.uuid

    url = f'/api/prestacoes-contas/iniciar/?conta_associacao_uuid={conta_associacao_uuid}&periodo_uuid={periodo_uuid}'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = PrestacaoContaLookUpSerializer(
        PrestacaoConta.objects.get(Q(conta_associacao__uuid=conta_associacao_uuid), Q(periodo__uuid=periodo_uuid)),
        many=False).data

    # Converto os campos UUIDs em strings para que a comparação funcione
    result_esperado['conta_associacao_uuid'] = f'{result_esperado["conta_associacao_uuid"]}'
    result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'

    assert response.status_code == status.HTTP_201_CREATED
    assert result == result_esperado


def test_api_inicia_prestacao_conta_sem_periodo(client, periodo, conta_associacao):
    conta_associacao_uuid = conta_associacao.uuid

    url = f'/api/prestacoes-contas/iniciar/?conta_associacao_uuid={conta_associacao_uuid}'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado


def test_api_inicia_prestacao_conta_sem_conta(client, periodo, conta_associacao):
    periodo_uuid = periodo.uuid

    url = f'/api/prestacoes-contas/iniciar/?periodo_uuid={periodo_uuid}'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado


def test_api_inicia_prestacao_conta_sem_parametros(client, periodo, conta_associacao):

    url = f'/api/prestacoes-contas/iniciar/'

    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado


def test_api_inicia_prestacao_conta_ja_iniciada(client, prestacao_conta):
    conta_associacao_uuid = prestacao_conta.conta_associacao.uuid
    periodo_uuid = prestacao_conta.periodo.uuid

    url = f'/api/prestacoes-contas/iniciar/?conta_associacao_uuid={conta_associacao_uuid}&periodo_uuid={periodo_uuid}'


    response = client.post(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'prestacao_ja_iniciada',
        'mensagem': 'Você não pode iniciar uma prestação de contas que já foi iniciada.'
    }

    assert response.status_code == status.HTTP_409_CONFLICT
    assert result == result_esperado
