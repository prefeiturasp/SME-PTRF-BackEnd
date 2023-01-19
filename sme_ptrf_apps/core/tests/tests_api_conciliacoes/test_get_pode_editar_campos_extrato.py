import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_pode_editar_campos_sem_pc(jwt_authenticated_client_a,
                                           associacao,
                                           periodo,
                                           conta_associacao,
                                           observacao_conciliacao
                                           ):
    conta_uuid = conta_associacao.uuid

    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={associacao.uuid}&periodo={periodo.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)
    resultado_esperado = {
        'permite_editar_campos_extrato': True
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado == result


def test_api_get_pode_editar_campos_com_pc_nao_devolvida(jwt_authenticated_client_a,
                                                         associacao,
                                                         periodo_2019_2,
                                                         conta_associacao,
                                                         observacao_conciliacao,
                                                         prestacao_conta_2019_2_conciliada
                                                         ):
    conta_uuid = conta_associacao.uuid
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={associacao.uuid}&periodo={periodo_2019_2.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)
    resultado_esperado = {
        'permite_editar_campos_extrato': False
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado == result


def test_api_get_pode_editar_campos_com_pc_devolvida_sem_ajuste_bancario(jwt_authenticated_client_a,
                                                                         associacao,
                                                                         periodo,
                                                                         conta_associacao,
                                                                         observacao_conciliacao,
                                                                         prestacao_conta_devolvida
                                                                         ):
    conta_uuid = conta_associacao.uuid
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={associacao.uuid}&periodo={periodo.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)
    resultado_esperado = {
        'permite_editar_campos_extrato': False
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado == result


def test_api_get_pode_editar_campos_com_pc_devolvida_com_ajuste_bancario(jwt_authenticated_client_a,
                                                                         associacao,
                                                                         periodo,
                                                                         conta_associacao_cheque,
                                                                         observacao_conciliacao,
                                                                         prestacao_conta_devolvida,
                                                                         analise_conta_prestacao_conta_2019_2,
                                                                         analise_prestacao_conta_2019_2
                                                                         ):
    conta_uuid = conta_associacao_cheque.uuid
    url = f'/api/conciliacoes/tem_ajuste_bancario/?associacao={associacao.uuid}&periodo={periodo.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)
    resultado_esperado = {
        'permite_editar_campos_extrato': True
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado == result

