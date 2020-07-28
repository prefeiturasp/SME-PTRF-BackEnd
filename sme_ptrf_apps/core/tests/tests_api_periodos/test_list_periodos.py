
import json
from datetime import datetime

import pytest
from freezegun import freeze_time
from rest_framework import status

from sme_ptrf_apps.core.models import Periodo

pytestmark = pytest.mark.django_db


def test_api_list_periodos(jwt_authenticated_client, periodo, periodo_anterior):
    response = jwt_authenticated_client.get('/api/periodos/', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo, periodo_anterior]
    expected_results = []
    for p in periodos:
        esperado = {
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "data_prevista_repasse": f'{p.data_prevista_repasse}' if p.data_prevista_repasse else None,
            "data_inicio_prestacao_contas": f'{p.data_inicio_prestacao_contas}' if p.data_inicio_prestacao_contas else None,
            "data_fim_prestacao_contas": f'{p.data_fim_prestacao_contas}' if p.data_fim_prestacao_contas else None,
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results


def test_api_list_periodos_lookup(jwt_authenticated_client, periodo, periodo_anterior):
    response = jwt_authenticated_client.get('/api/periodos/lookup/', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo, periodo_anterior]
    expected_results = []
    for p in periodos:
        esperado = {
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "referencia_por_extenso": f"{p.referencia.split('.')[1]}° repasse de {p.referencia.split('.')[0]}"
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results


@freeze_time('2020-06-14 10:11:12')
def test_api_list_periodos_lookup_until_now(jwt_authenticated_client, periodo, periodo_anterior, periodo_futuro):
    """O esperado é que o periodo_futuro não esteja na lista de resultados."""   
    response = jwt_authenticated_client.get('/api/periodos/lookup-until-now/', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo, periodo_anterior]
    expected_results = []
    for p in periodos:
        esperado = {
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "referencia_por_extenso": f"{p.referencia.split('.')[1]}° repasse de {p.referencia.split('.')[0]}"
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results
