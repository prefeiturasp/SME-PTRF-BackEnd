import json

import pytest

from django.core.serializers.json import DjangoJSONEncoder
from unittest.mock import patch
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_update_retificacao_consolidado_dre(
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
    }

    with patch('sme_ptrf_apps.dre.services.consolidado_dre_service.update_retificacao') as mock_update_retificacao_consolidado_dre:
        response = jwt_authenticated_client_dre.post(
            f'/api/consolidados-dre/{retificacao_uuid}/update_retificacao/',
            data=json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        mock_update_retificacao_consolidado_dre.assert_called_once_with(
            retificacao=retificacao_dre_teste_api_consolidado_dre,
            prestacoes_de_conta_a_retificar=payload['lista_pcs'],
            motivo=payload['motivo'],
        )

        assert response.status_code == status.HTTP_200_OK


def test_update_retificacao_consolidado_dre_sem_informar_pcs_deve_retornar_400(
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
    }

    response = jwt_authenticated_client_dre.post(
        f'/api/consolidados-dre/{retificacao_uuid}/update_retificacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'lista_pcs': ['É necessário informar ao menos uma PC para retificar.']}


def test_update_retificacao_consolidado_dre_sem_informar_motivo_deve_retornar_400__motivo_nao_eh_mais_obrigatorio(
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
    }

    response = jwt_authenticated_client_dre.post(
        f'/api/consolidados-dre/{retificacao_uuid}/update_retificacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

