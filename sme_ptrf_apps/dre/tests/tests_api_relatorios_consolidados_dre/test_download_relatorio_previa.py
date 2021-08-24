import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_geracao_e_download_relatorio_previa(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):

    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': str(periodo.uuid),
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': True
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/previa/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'OK': 'Relatório Consolidado na fila para processamento.'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_201_CREATED


def test_api_geracao_relatorio_previa_sem_dre_uuid(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': '',
        'periodo_uuid': str(periodo.uuid),
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/previa/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre, período, conta e parcial.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_geracao_relatorio_previa_sem_periodo_uuid(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': '',
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/previa/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre, período, conta e parcial.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
