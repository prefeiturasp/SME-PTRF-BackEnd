import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_publicar_consolidado_dre(dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre):
    payload = {
        'dre_uuid': f'{dre_teste_api_consolidado_dre.uuid}',
        'periodo_uuid': f'{periodo_teste_api_consolidado_dre.uuid}',
    }
    return payload


def test_gerar_previa_consolidado_dre_ata_preenchida_deve_passar(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    payload_publicar_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api_preenchida
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-previa/',
        data=json.dumps(payload_publicar_consolidado_dre),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert result['versao'] == 'PREVIA'

    assert ConsolidadoDRE.objects.filter(uuid=result['uuid']).exists()


def test_gerar_previa_consolidado_dre_ata_nao_prenchida_deve_passar(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    payload_publicar_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-previa/',
        data=json.dumps(payload_publicar_consolidado_dre),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert result['versao'] == 'PREVIA'

    assert ConsolidadoDRE.objects.filter(uuid=result['uuid']).exists()


def test_gerar_previa_consolidado_dre_sem_periodo_uuid(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    payload = {
        'dre_uuid': str(dre_teste_api_consolidado_dre.uuid),
        'periodo_uuid': '',
        'parcial': False
    }

    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-previa/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre e período'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_gerar_previa_consolidado_dre_sem_dre_uuid(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    payload = {
        'dre_uuid': '',
        'periodo_uuid': f"{periodo_teste_api_consolidado_dre.uuid}",
        'parcial': False
    }

    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-previa/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre e período'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_gerar_previa_consolidado_dre_objeto_nao_encontrado(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    import uuid
    uuid_objeto = str(uuid.uuid4())
    payload = {
        'dre_uuid': str(dre_teste_api_consolidado_dre.uuid),
        'periodo_uuid': uuid_objeto,
    }

    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/gerar-previa/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)
    esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': 'O objeto período para o uuid '
                    f'{uuid_objeto} não foi encontrado na base.',
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
