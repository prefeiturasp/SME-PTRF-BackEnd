import json

import pytest
from rest_framework import status

from ...api.serializers import ReceitaListaSerializer
from ...models import Receita
from ....despesas.models import Despesa
from ....despesas.status_cadastro_completo import STATUS_COMPLETO

pytestmark = pytest.mark.django_db


def test_api_atrelar_saida_do_recurso(
    jwt_authenticated_client_p,
    receita_saida_recurso,
    despesa_saida_recurso,
    rateio_saida_recurso
):
    receita_uuid = receita_saida_recurso.uuid
    despesa_uuid = despesa_saida_recurso.uuid

    url = f'/api/receitas/{receita_uuid}/atrelar-saida-recurso/?despesa_uuid={despesa_uuid}'

    response = jwt_authenticated_client_p.patch(url, content_type='application/json')

    result = json.loads(response.content)

    receita_atrelada = Receita.by_uuid(receita_uuid)

    result_esperado = ReceitaListaSerializer(receita_atrelada, many=False).data
    result_esperado['saida_do_recurso']['associacao'] = str(result_esperado['saida_do_recurso']['associacao'])
    result_esperado['acao_associacao'] = dict(result_esperado["acao_associacao"])
    result_esperado['acao_associacao'] = dict(result_esperado["acao_associacao"])
    result_esperado['conta_associacao'] = dict(result_esperado["conta_associacao"])
    result_esperado['detalhe_tipo_receita'] = dict(result_esperado["detalhe_tipo_receita"])
    result_esperado['saida_do_recurso'] = dict(result_esperado["saida_do_recurso"])
    result_esperado['saida_do_recurso']['tipo_documento'] = dict(result_esperado["saida_do_recurso"]['tipo_documento'])
    result_esperado['saida_do_recurso']['valor_ptrf'] = 100.00
    result_esperado['tipo_receita'] = dict(result_esperado["tipo_receita"])

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

    despesa_atrelada = Despesa.by_uuid(despesa_uuid)
    assert despesa_atrelada.status == STATUS_COMPLETO

    rateio_atrelado = despesa_atrelada.rateios.first()
    assert rateio_atrelado.status == STATUS_COMPLETO


def test_api_atrelar_saida_do_recurso_uuid_receita_incorreto(jwt_authenticated_client_p):
    uuid_incorreto = '99999944444444'

    url = f'/api/receitas/{uuid_incorreto}/atrelar-saida-recurso/'

    response = jwt_authenticated_client_p.patch(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': f"O objeto receita para o uuid {uuid_incorreto} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_atrelar_saida_do_recurso_sem_uuid_despesa(jwt_authenticated_client_p, receita_saida_recurso):

    url = f'/api/receitas/{receita_saida_recurso.uuid}/atrelar-saida-recurso/'

    response = jwt_authenticated_client_p.patch(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da despesa'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_atrelar_saida_do_recurso_uuid_despesa_incorreto(jwt_authenticated_client_p, receita_saida_recurso):
    uuid_incorreto = '99999944444444'

    url = f'/api/receitas/{receita_saida_recurso.uuid}/atrelar-saida-recurso/?despesa_uuid={uuid_incorreto}'

    response = jwt_authenticated_client_p.patch(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': f"O objeto despesa para o uuid {uuid_incorreto} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado
