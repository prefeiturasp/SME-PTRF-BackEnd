import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_passar_para_status_sme_publicado(consolidado_dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre):
    payload = {
        'consolidado_dre': f'{consolidado_dre_teste_api_consolidado_dre.uuid}',
        "data_publicacao": "2022-09-30",
        "pagina_publicacao": "05 e 06"
    }
    return payload


@pytest.fixture
def payload_passar_para_status_sme_publicado_consolidado_inexistente(consolidado_dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre):
    payload = {
        'consolidado_dre': f'{consolidado_dre_teste_api_consolidado_dre.uuid}XX',
        "data_publicacao": "2022-09-30",
        "pagina_publicacao": "05 e 06"
    }
    return payload


@pytest.fixture
def payload_passar_para_status_sme_publicado_sem_data_publicacao(consolidado_dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre):
    payload = {
        'consolidado_dre': f'{consolidado_dre_teste_api_consolidado_dre.uuid}',
        "data_publicacao": "",
        "pagina_publicacao": "05 e 06"
    }
    return payload


@pytest.fixture
def payload_passar_para_status_sme_publicado_sem_pagina_publicacao(consolidado_dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre):
    payload = {
        'consolidado_dre': f'{consolidado_dre_teste_api_consolidado_dre.uuid}',
        "data_publicacao": "2022-09-30",
        "pagina_publicacao": ""
    }
    return payload


def test_passar_relatorio_para_status_sme_publicado(
    jwt_authenticated_client_dre,
    payload_passar_para_status_sme_publicado,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api_preenchida,
    unidade_teste_api_consolidado_dre_01,
    associacao_teste_api_consolidado_dre_01,
    unidade_teste_api_consolidado_dre_02,
    associacao_teste_api_consolidado_dre_02
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/marcar-como-publicado-no-diario-oficial/',
        data=json.dumps(payload_passar_para_status_sme_publicado),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert ConsolidadoDRE.objects.filter(uuid=result['uuid']).exists()

    assert result['status_sme'] == 'PUBLICADO'
    assert result['data_publicacao'] == '2022-09-30'
    assert result['pagina_publicacao'] == '05 e 06'


def test_passar_relatorio_para_status_sme_publicado_consolidado_inexistente(
    jwt_authenticated_client_dre,
    payload_passar_para_status_sme_publicado_consolidado_inexistente,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api_preenchida,
    unidade_teste_api_consolidado_dre_01,
    associacao_teste_api_consolidado_dre_01,
    unidade_teste_api_consolidado_dre_02,
    associacao_teste_api_consolidado_dre_02
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/marcar-como-publicado-no-diario-oficial/',
        data=json.dumps(payload_passar_para_status_sme_publicado_consolidado_inexistente),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_passar_relatorio_para_status_sme_publicado_sem_data_publicacao(
    jwt_authenticated_client_dre,
    payload_passar_para_status_sme_publicado_sem_data_publicacao,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api_preenchida,
    unidade_teste_api_consolidado_dre_01,
    associacao_teste_api_consolidado_dre_01,
    unidade_teste_api_consolidado_dre_02,
    associacao_teste_api_consolidado_dre_02
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/marcar-como-publicado-no-diario-oficial/',
        data=json.dumps(payload_passar_para_status_sme_publicado_sem_data_publicacao),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_passar_relatorio_para_status_sme_publicado_sem_pagina_publicacao(
    jwt_authenticated_client_dre,
    payload_passar_para_status_sme_publicado_sem_pagina_publicacao,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api_preenchida,
    unidade_teste_api_consolidado_dre_01,
    associacao_teste_api_consolidado_dre_01,
    unidade_teste_api_consolidado_dre_02,
    associacao_teste_api_consolidado_dre_02
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/marcar-como-publicado-no-diario-oficial/',
        data=json.dumps(payload_passar_para_status_sme_publicado_sem_pagina_publicacao),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_passar_relatorio_para_status_sme_nao_publicado(
    jwt_authenticated_client_dre,
    payload_passar_para_status_sme_publicado,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api_preenchida,
    unidade_teste_api_consolidado_dre_01,
    associacao_teste_api_consolidado_dre_01,
    unidade_teste_api_consolidado_dre_02,
    associacao_teste_api_consolidado_dre_02
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/marcar-como-nao-publicado-no-diario-oficial/',
        data=json.dumps(payload_passar_para_status_sme_publicado),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    assert ConsolidadoDRE.objects.filter(uuid=result['uuid']).exists()

    assert result['status_sme'] == 'NAO_PUBLICADO'
    assert result['data_publicacao'] == None
    assert result['pagina_publicacao'] == ''


def test_passar_relatorio_para_status_sme_nao_publicado_consolidado_inexistente(
    jwt_authenticated_client_dre,
    payload_passar_para_status_sme_publicado_consolidado_inexistente,
    consolidado_dre_teste_api_consolidado_dre,
    ano_analise_regularidade_2022_teste_api,
    ata_parecer_tecnico_teste_api_preenchida,
    unidade_teste_api_consolidado_dre_01,
    associacao_teste_api_consolidado_dre_01,
    unidade_teste_api_consolidado_dre_02,
    associacao_teste_api_consolidado_dre_02
):
    response = jwt_authenticated_client_dre.post(
        '/api/consolidados-dre/marcar-como-nao-publicado-no-diario-oficial/',
        data=json.dumps(payload_passar_para_status_sme_publicado_consolidado_inexistente),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


