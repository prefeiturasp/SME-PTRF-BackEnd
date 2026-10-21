import json
from uuid import uuid4

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_tem_ajuste_bancario_sem_associacao(jwt_authenticated_client_a, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/tem_ajuste_bancario/?periodo={periodo_2020_1.uuid}'
    url += f'&conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_tem_ajuste_bancario_associacao_nao_encontrada(
        jwt_authenticated_client_a, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={uuid4()}&periodo={periodo_2020_1.uuid}'
    url += f'&conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_tem_ajuste_bancario_sem_periodo(jwt_authenticated_client_a, conta_associacao_cartao):
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={conta_associacao_cartao.associacao.uuid}'
    url += f'&conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_tem_ajuste_bancario_periodo_nao_encontrado(jwt_authenticated_client_a, conta_associacao_cartao):
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={conta_associacao_cartao.associacao.uuid}'
    url += f'&periodo={uuid4()}&conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_tem_ajuste_bancario_sem_conta_associacao(jwt_authenticated_client_a, periodo_2020_1, associacao):
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={associacao.uuid}&periodo={periodo_2020_1.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_tem_ajuste_bancario_conta_associacao_nao_encontrada(jwt_authenticated_client_a, periodo_2020_1, associacao):
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={associacao.uuid}&periodo={periodo_2020_1.uuid}'
    url += f'&conta_associacao={uuid4()}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_tem_ajuste_bancario_sucesso(jwt_authenticated_client_a, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={conta_associacao_cartao.associacao.uuid}'
    url += f'&periodo={periodo_2020_1.uuid}&conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert 'permite_editar_campos_extrato' in json.loads(response.content)
