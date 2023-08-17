import json

import pytest
from rest_framework import status

from ...tipos_aplicacao_recurso import APLICACAO_CUSTEIO, APLICACAO_CAPITAL, APLICACAO_NOMES

pytestmark = pytest.mark.django_db


def test_api_get_despesas_tabelas(associacao, jwt_authenticated_client_d, tipo_aplicacao_recurso, tipo_custeio, tipo_documento, tipo_transacao, acao,
                                  acao_associacao, tipo_conta, conta_associacao, tag_ativa):
    response = jwt_authenticated_client_d.get(f'/api/despesas/tabelas/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    assert len(result['tipos_aplicacao_recurso']) == 2
    assert len(result['tipos_custeio']) == 1
    assert len(result['tipos_documento']) == 1
    assert len(result['tipos_transacao']) == 1
    assert len(result['acoes_associacao']) == 1
    assert len(result['contas_associacao']) == 1
    assert len(result['tags']) == 1

    assert response.status_code == status.HTTP_200_OK

def test_api_get_despesas_tabelas_sem_permissao(associacao, jwt_authenticated_client_sem_permissao, tipo_aplicacao_recurso, tipo_custeio, tipo_documento, tipo_transacao, acao,
                                  acao_associacao, tipo_conta, conta_associacao, tag_ativa):
    response = jwt_authenticated_client_sem_permissao.get(f'/api/despesas/tabelas/?associacao_uuid={associacao.uuid}', content_type='application/json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
