import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_search_receitas_por_nome_detalhe_outros(jwt_authenticated_client, tipo_receita,
                                                         receita_xxx_estorno,
                                                         receita_yyy_repasse,
                                                         acao,
                                                         acao_associacao,
                                                         associacao,
                                                         tipo_conta,
                                                         conta_associacao):
    response = jwt_authenticated_client.get(f'/api/receitas/?associacao__uuid={associacao.uuid}&search=XXXÇ',
                                            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_search_receitas_por_nome_detalhe_tipo_receita(jwt_authenticated_client,
                                                               tipo_receita,
                                                               detalhe_tipo_receita,
                                                               receita_xxx_estorno,
                                                               receita_yyy_repasse,
                                                               acao,
                                                               acao_associacao,
                                                               associacao,
                                                               tipo_conta,
                                                               conta_associacao):
    response = jwt_authenticated_client.get(f'/api/receitas/?associacao__uuid={associacao.uuid}&search=yyyÇ',
                                            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_search_receitas_por_nome_detalhe_outros_ignora_acentos(jwt_authenticated_client, tipo_receita,
                                                                        receita_xxx_estorno,
                                                                        receita_yyy_repasse,
                                                                        acao,
                                                                        acao_associacao,
                                                                        associacao,
                                                                        tipo_conta,
                                                                        conta_associacao):
    response = jwt_authenticated_client.get(f'/api/receitas/?associacao__uuid={associacao.uuid}&search=XXXc',
                                            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_search_receitas_por_nome_detalhe_tipo_receita_ignora_acento(jwt_authenticated_client,
                                                                             tipo_receita,
                                                                             detalhe_tipo_receita,
                                                                             receita_xxx_estorno,
                                                                             receita_yyy_repasse,
                                                                             acao,
                                                                             acao_associacao,
                                                                             associacao,
                                                                             tipo_conta,
                                                                             conta_associacao):
    response = jwt_authenticated_client.get(f'/api/receitas/?associacao__uuid={associacao.uuid}&search=yyyc',
                                            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
