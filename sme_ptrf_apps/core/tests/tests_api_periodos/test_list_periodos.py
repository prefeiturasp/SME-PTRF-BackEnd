import json
import pytest
from freezegun import freeze_time
from rest_framework import status

from .conftest import UUID_RECURSO_A

pytestmark = pytest.mark.django_db


def test_api_list_periodos(jwt_authenticated_client, periodo_2020_4, periodo_2021_1, periodo_2021_2, recurso_esperado):
    response = jwt_authenticated_client.get('/api/periodos/', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo_2021_2, periodo_2021_1, periodo_2020_4]
    expected_results = []
    for p in periodos:
        esperado = {
            "id": p.id,
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "data_prevista_repasse": f'{p.data_prevista_repasse}' if p.data_prevista_repasse else None,
            "data_inicio_prestacao_contas": f'{p.data_inicio_prestacao_contas}' if p.data_inicio_prestacao_contas else None,
            "data_fim_prestacao_contas": f'{p.data_fim_prestacao_contas}' if p.data_fim_prestacao_contas else None,
            "editavel": p.editavel,
            "periodo_anterior": {
                "id": p.periodo_anterior.id,
                "uuid": f'{p.periodo_anterior.uuid}',
                "referencia": p.periodo_anterior.referencia,
                "data_inicio_realizacao_despesas": f'{p.periodo_anterior.data_inicio_realizacao_despesas}' if p.periodo_anterior.data_inicio_realizacao_despesas else None,
                "data_fim_realizacao_despesas": f'{p.periodo_anterior.data_fim_realizacao_despesas}' if p.periodo_anterior.data_fim_realizacao_despesas else None,
                "referencia_por_extenso": f"{p.periodo_anterior.referencia.split('.')[1]}° repasse de {p.periodo_anterior.referencia.split('.')[0]}",
                "recurso": recurso_esperado(p.periodo_anterior.recurso),
            } if p.periodo_anterior else None,
            "recurso": recurso_esperado(p.recurso),
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results


def test_api_list_periodos_lookup(jwt_authenticated_client, periodo, periodo_anterior, recurso_esperado):
    response = jwt_authenticated_client.get('/api/periodos/lookup/', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo, periodo_anterior]
    expected_results = []
    for p in periodos:
        esperado = {
            "id": p.id,
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "referencia_por_extenso": f"{p.referencia.split('.')[1]}° repasse de {p.referencia.split('.')[0]}",
            "recurso": recurso_esperado(p.recurso),
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results


@freeze_time('2020-06-14 10:11:12')
def test_api_list_periodos_lookup_until_now(jwt_authenticated_client, periodo, periodo_anterior, periodo_futuro, recurso_esperado):
    """O esperado é que o periodo_futuro não esteja na lista de resultados."""
    response = jwt_authenticated_client.get('/api/periodos/lookup-until-now/', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo, periodo_anterior]
    expected_results = []
    for p in periodos:
        esperado = {
            "id": p.id,
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "referencia_por_extenso": f"{p.referencia.split('.')[1]}° repasse de {p.referencia.split('.')[0]}",
            "recurso": recurso_esperado(p.recurso),
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results


def test_api_list_periodos_por_referencia(jwt_authenticated_client, periodo_2020_4, periodo_2021_1, periodo_2021_2, recurso_esperado):
    response = jwt_authenticated_client.get('/api/periodos/?referencia=2021', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo_2021_2, periodo_2021_1]
    expected_results = []
    for p in periodos:
        esperado = {
            "id": p.id,
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "data_prevista_repasse": f'{p.data_prevista_repasse}' if p.data_prevista_repasse else None,
            "data_inicio_prestacao_contas": f'{p.data_inicio_prestacao_contas}' if p.data_inicio_prestacao_contas else None,
            "data_fim_prestacao_contas": f'{p.data_fim_prestacao_contas}' if p.data_fim_prestacao_contas else None,
            "editavel": p.editavel,
            "periodo_anterior": {
                'id': p.periodo_anterior.id,
                'referencia': p.periodo_anterior.referencia,
                'data_inicio_realizacao_despesas': f'{p.periodo_anterior.data_inicio_realizacao_despesas}',
                'data_fim_realizacao_despesas': f'{p.periodo_anterior.data_fim_realizacao_despesas}',
                'referencia_por_extenso': f'{p.periodo_anterior.referencia_por_extenso}',
                'uuid': f'{p.periodo_anterior.uuid}',
                "recurso": recurso_esperado(p.periodo_anterior.recurso),
            } if p.periodo_anterior else None,
            "recurso": recurso_esperado(p.recurso),
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results


def test_api_list_periodos_por_associacao(jwt_authenticated_client, prestacao_conta_2021_1_aprovada_associacao_encerrada, periodo_2021_1, periodo_2021_2, recurso_esperado):
    response = jwt_authenticated_client.get(
        f'/api/periodos/?associacao_uuid={prestacao_conta_2021_1_aprovada_associacao_encerrada.associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    periodos = [periodo_2021_1]
    expected_results = []
    for p in periodos:
        esperado = {
            "id": p.id,
            "uuid": f'{p.uuid}',
            "referencia": p.referencia,
            "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
            "data_prevista_repasse": f'{p.data_prevista_repasse}' if p.data_prevista_repasse else None,
            "data_inicio_prestacao_contas": f'{p.data_inicio_prestacao_contas}' if p.data_inicio_prestacao_contas else None,
            "data_fim_prestacao_contas": f'{p.data_fim_prestacao_contas}' if p.data_fim_prestacao_contas else None,
            "editavel": p.editavel,
            "periodo_anterior": {
                'id': p.periodo_anterior.id,
                'uuid': f'{p.periodo_anterior.uuid}',
                'referencia': p.periodo_anterior.referencia,
                'data_inicio_realizacao_despesas': f'{p.periodo_anterior.data_inicio_realizacao_despesas}',
                'data_fim_realizacao_despesas': f'{p.periodo_anterior.data_fim_realizacao_despesas}',
                'referencia_por_extenso': f'{p.periodo_anterior.referencia_por_extenso}',
                "recurso": recurso_esperado(p.periodo_anterior.recurso),
            } if p.periodo_anterior else None,
            "recurso": recurso_esperado(p.recurso),
        }
        expected_results.append(esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results


def test_api_list_periodos_por_recurso_selecionado(jwt_authenticated_client, periodo_2020_4_com_recurso_a, periodo_2021_1_com_recurso_a, periodo_2021_2_com_recurso_legado_ptrf):
    response = jwt_authenticated_client.get('/api/periodos/', content_type='application/json', HTTP_X_RECURSO_SELECIONADO=UUID_RECURSO_A)
    result = json.loads(response.content)

    periodos = [
        periodo_2021_2_com_recurso_legado_ptrf,
        periodo_2021_1_com_recurso_a,
        periodo_2020_4_com_recurso_a
    ]
    total_periodos_recurso_a = []
    for p in periodos:
        if p.recurso and str(p.recurso.uuid) == UUID_RECURSO_A:
            total_periodos_recurso_a.append(p)

    assert response.status_code == status.HTTP_200_OK
    assert len(total_periodos_recurso_a) == len(result)

