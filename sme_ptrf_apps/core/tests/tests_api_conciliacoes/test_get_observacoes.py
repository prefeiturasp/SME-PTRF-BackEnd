import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_observacoes_lista_vazia(client,
                                         periodo_2020_1,
                                         conta_associacao_cartao
                                         ):
    conta_uuid = conta_associacao_cartao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == []


def test_api_get_observacoes(client,
                             periodo,
                             conta_associacao,
                             observacao_conciliacao
                             ):
    conta_uuid = conta_associacao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo.uuid}&conta_associacao={conta_uuid}'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == [
        {
            'acao_associacao_uuid': f'{observacao_conciliacao.acao_associacao.uuid}',
            'observacao': 'Uma bela observação.'
        }
    ]
