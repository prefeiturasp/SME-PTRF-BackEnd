import json

import pytest

from django.core.serializers.json import DjangoJSONEncoder
from unittest.mock import patch
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_desfazer_retificacao_consolidado_dre_nao_deve_apagar_retificacao(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    retificacao_dre_teste_api_consolidado_dre,
    prestacao_conta_x,
):
    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    payload = {
        'lista_pcs': [prestacao_conta_x.uuid],
        'motivo': 'Motivo de retificação novo',
        'deve_apagar_retificacao': False
    }

    with patch('sme_ptrf_apps.dre.services.consolidado_dre_service.desfazer_retificacao_dre') as mock_desfazer_retificacao_consolidado_dre:
        response = jwt_authenticated_client_dre.post(
            f'/api/consolidados-dre/{retificacao_uuid}/desfazer_retificacao/',
            data=json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        mock_desfazer_retificacao_consolidado_dre.assert_called_once_with(
            retificacao=retificacao_dre_teste_api_consolidado_dre,
            prestacoes_de_conta_a_desfazer_retificacao=payload['lista_pcs'],
            motivo=payload['motivo'],
            deve_apagar_retificacao=payload['deve_apagar_retificacao']
        )

        assert response.status_code == status.HTTP_200_OK


def test_desfazer_retificacao_consolidado_dre_deve_apagar_retificacao(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    retificacao_dre_teste_api_consolidado_dre,
    prestacao_conta_x,
):
    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    payload = {
        'lista_pcs': [prestacao_conta_x.uuid],
        'motivo': 'Motivo de retificação novo',
        'deve_apagar_retificacao': True
    }

    with patch('sme_ptrf_apps.dre.services.consolidado_dre_service.desfazer_retificacao_dre') as mock_desfazer_retificacao_consolidado_dre:
        response = jwt_authenticated_client_dre.post(
            f'/api/consolidados-dre/{retificacao_uuid}/desfazer_retificacao/',
            data=json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        mock_desfazer_retificacao_consolidado_dre.assert_called_once_with(
            retificacao=retificacao_dre_teste_api_consolidado_dre,
            prestacoes_de_conta_a_desfazer_retificacao=payload['lista_pcs'],
            motivo=payload['motivo'],
            deve_apagar_retificacao=payload['deve_apagar_retificacao']
        )

        assert response.status_code == status.HTTP_200_OK


def test_desfazer_retificacao_consolidado_dre_sem_informar_pcs_deve_retornar_400(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    retificacao_dre_teste_api_consolidado_dre,
    prestacao_conta_x,
):
    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    payload = {
        'lista_pcs': [],
        'motivo': 'Motivo de retificação',
        'deve_apagar_retificacao': False
    }

    response = jwt_authenticated_client_dre.post(
        f'/api/consolidados-dre/{retificacao_uuid}/desfazer_retificacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'lista_pcs': ['É necessário informar ao menos uma PC para retificar.']}


def test_desfazer_retificacao_consolidado_dre_sem_informar_motivo_deve_retornar_400(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    retificacao_dre_teste_api_consolidado_dre,
    prestacao_conta_x,
):
    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    payload = {
        'lista_pcs': [f'{prestacao_conta_x.uuid}'],
        'motivo': '',
        'deve_apagar_retificacao': False
    }

    response = jwt_authenticated_client_dre.post(
        f'/api/consolidados-dre/{retificacao_uuid}/desfazer_retificacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'motivo': ['This field may not be blank.']}


def test_desfazer_retificacao_consolidado_dre_sem_informar_deve_apagar_retificacao_deve_retornar_400(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    retificacao_dre_teste_api_consolidado_dre,
    prestacao_conta_x,
):
    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    payload = {
        'lista_pcs': [f'{prestacao_conta_x.uuid}'],
        'motivo': 'teste',
    }

    response = jwt_authenticated_client_dre.post(
        f'/api/consolidados-dre/{retificacao_uuid}/desfazer_retificacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'deve_apagar_retificacao': ['This field is required.']}
