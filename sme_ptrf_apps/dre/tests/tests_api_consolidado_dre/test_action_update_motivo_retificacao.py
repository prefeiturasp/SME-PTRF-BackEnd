import pytest
import json
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_patch_alterar_motivo_retificacao(
    jwt_authenticated_client_dre,
    retificacao_dre_teste_api_consolidado_dre,
):
    payload = {
        'motivo': 'motivo retificação',
    }

    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.patch(
        f'/api/consolidados-dre/{retificacao_uuid}/update_motivo_retificacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_update_motivo_retificacao_em_branco_deve_retornar_400__motivo_nao_eh_mais_obrigatorio(
    jwt_authenticated_client_dre,
    retificacao_dre_teste_api_consolidado_dre,
):
    retificacao_uuid = retificacao_dre_teste_api_consolidado_dre.uuid

    payload = {
        'motivo': '',
    }

    response = jwt_authenticated_client_dre.patch(
        f'/api/consolidados-dre/{retificacao_uuid}/update_motivo_retificacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

