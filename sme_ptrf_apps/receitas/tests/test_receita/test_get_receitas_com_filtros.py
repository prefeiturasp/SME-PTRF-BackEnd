import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_receitas_por_tipo_receita(jwt_authenticated_client,
                                           tipo_receita_estorno,
                                           tipo_receita_repasse,
                                           receita_xxx_estorno,
                                           receita_yyy_repasse,
                                           acao,
                                           acao_associacao,
                                           associacao,
                                           tipo_conta,
                                           conta_associacao):
    response = jwt_authenticated_client.get(f'/api/receitas/?tipo_receita={tipo_receita_estorno.id}',
                          content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_receitas_por_acao_associacao(jwt_authenticated_client,
                                              tipo_receita_estorno,
                                              tipo_receita_repasse,
                                              receita_xxx_estorno,
                                              receita_yyy_repasse,
                                              acao,
                                              acao_associacao_ptrf,
                                              acao_associacao_role_cultural,
                                              associacao,
                                              tipo_conta,
                                              conta_associacao):
    response = jwt_authenticated_client.get(
        f'/api/receitas/?associacao__uuid={associacao.uuid}&acao_associacao__uuid={acao_associacao_ptrf.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_receitas_por_conta_associacao(jwt_authenticated_client,
                                               tipo_receita_estorno,
                                               tipo_receita_repasse,
                                               receita_xxx_estorno,
                                               receita_yyy_repasse,
                                               acao,
                                               acao_associacao_ptrf,
                                               acao_associacao_role_cultural,
                                               associacao,
                                               tipo_conta,
                                               conta_associacao_cheque,
                                               conta_associacao_cartao):
    response = jwt_authenticated_client.get(
        f'/api/receitas/?associacao__uuid={associacao.uuid}&conta_associacao__uuid={conta_associacao_cartao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
