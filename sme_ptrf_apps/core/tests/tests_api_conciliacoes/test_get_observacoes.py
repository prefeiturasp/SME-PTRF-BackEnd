import json

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

pytestmark = pytest.mark.django_db


def test_api_get_observacoes_lista_vazia(jwt_authenticated_client_a,
                                         periodo_2020_1,
                                         conta_associacao_cartao
                                         ):
    conta_uuid = conta_associacao_cartao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {}


def test_api_get_observacoes(jwt_authenticated_client_a,
                             periodo,
                             conta_associacao,
                             observacao_conciliacao
                             ):
    conta_uuid = conta_associacao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
        'comprovante_extrato': '',
        'data_atualizacao_comprovante_extrato': None,
        'observacao': 'Uma bela observação.',
        'data_extrato': '2020-07-01',
        'saldo_extrato': 1000.0
    }
