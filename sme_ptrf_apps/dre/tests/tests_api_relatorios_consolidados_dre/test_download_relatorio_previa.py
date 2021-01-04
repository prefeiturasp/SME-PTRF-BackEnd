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

    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=relatorio_consolidado_dre.xlsx'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.status_code == status.HTTP_200_OK


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
