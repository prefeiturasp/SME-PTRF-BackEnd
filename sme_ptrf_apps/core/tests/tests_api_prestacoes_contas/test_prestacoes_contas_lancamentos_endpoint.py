import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_lancamentos_url_com_parametros_minimos(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == []


def test_lancamentos_url_com_parametro_opcional_acao_associacao_valido(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
    acao_associacao,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&acao_associacao={acao_associacao.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == []


def test_lancamentos_url_com_parametro_opcional_tipo_transacao_valido(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&tipo=GASTOS'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == []


def test_lancamentos_url_com_parametro_opcional_ordenar_por_imposto_valido(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&ordenar_por_imposto=true'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == []


def test_lancamentos_url_com_parametro_opcional_filtrar_por_tipo_de_documento_valido(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
    tipo_documento,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&filtrar_por_tipo_de_documento={tipo_documento.id}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == []


def test_lancamentos_url_com_parametro_opcional_filtrar_por_tipo_de_pagamento_valido(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
    tipo_transacao,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&filtrar_por_tipo_de_pagamento={tipo_transacao.id}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == []



def test_lancamentos_url_deve_exigir_analise_prestacao(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    conta_associacao,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?conta_associacao={conta_associacao.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content) == {'analise_prestacao': ['This field is required.']}


def test_lancamentos_url_deve_exigir_conta_associacao(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'conta_associacao' in json.loads(response.content).keys()


def test_lancamentos_url_deve_exigir_analise_prestacao_pertencente_a_prestacao_de_contas(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
    prestacao_conta_iniciada,
):
    url = f'/api/prestacoes-contas/{prestacao_conta_iniciada.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'analise_prestacao' in json.loads(response.content).keys()


def test_lancamentos_url_deve_exigir_uuid_analise_prestacao_valido(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    conta_associacao,
):
    fake_uuid = '00000000-0000-0000-0000-000000000000'
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={fake_uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_lancamentos_url_deve_exigir_uuid_conta_associacao_valido(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
):
    fake_uuid = '00000000-0000-0000-0000-000000000000'
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={fake_uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_lancamentos_url_deve_exigir_uuid_acao_associacao_valida_quando_passado(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
    acao_associacao,
):
    fake_uuid = '00000000-0000-0000-0000-000000000000'
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&acao_associacao={fake_uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_lancamentos_url_deve_exigir_tipo_transacao_valido_quando_passado(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
    acao_associacao,
):
    fake_tipo = 'fake'
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&acao_associacao={acao_associacao.uuid}'
    url += f'&tipo={fake_tipo}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_lancamentos_url_deve_exigir_ordenar_por_imposto_bollean_quando_passado(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
):
    fake_ordenar_por_imposto = 'fake'
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&ordenar_por_imposto={fake_ordenar_por_imposto}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_lancamentos_url_deve_exigir_tipo_documento_valido_quando_passado(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
):
    fake_tipo_documento_id = 7646574
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&filtrar_por_tipo_de_documento={fake_tipo_documento_id}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_lancamentos_url_deve_exigir_tipo_pagamento_valido_quando_passado(
    jwt_authenticated_client_a,
    prestacao_conta_com_analise_anterior,
    analise_prestacao_conta_anterior,
    conta_associacao,
):
    fake_tipo_pagamento_id = 7646574
    url = f'/api/prestacoes-contas/{prestacao_conta_com_analise_anterior.uuid}/lancamentos/'
    url += f'?analise_prestacao={analise_prestacao_conta_anterior.uuid}'
    url += f'&conta_associacao={conta_associacao.uuid}'
    url += f'&filtrar_por_tipo_de_pagamento={fake_tipo_pagamento_id}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
