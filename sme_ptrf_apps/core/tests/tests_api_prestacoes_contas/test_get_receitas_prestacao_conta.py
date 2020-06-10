import json

import pytest
from rest_framework import status

from ....receitas.api.serializers import ReceitaListaSerializer

pytestmark = pytest.mark.django_db


def test_api_get_receitas_conferidasprestacao_conta(client,
                                                    acao_associacao_role_cultural,
                                                    prestacao_conta_iniciada,
                                                    receita_2019_2_role_repasse_conferida,
                                                    receita_2020_1_role_repasse_conferida,
                                                    receita_2020_1_role_repasse_nao_conferida,
                                                    receita_2020_1_ptrf_repasse_conferida,
                                                    receita_2020_1_role_repasse_cheque_conferida
                                                    ):
    prestacao_uuid = prestacao_conta_iniciada.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/receitas/?acao_associacao_uuid={acao_uuid}&conferido=True'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = []
    result_esperado = ReceitaListaSerializer(receita_2020_1_role_repasse_conferida, many=False).data
    resultado_esperado.append(result_esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de receitas esperada."


def test_api_get_receitas_nao_conferidas_prestacao_conta(client,
                                                         acao_associacao_role_cultural,
                                                         prestacao_conta_iniciada,
                                                         receita_2019_2_role_repasse_conferida,
                                                         receita_2020_1_role_repasse_conferida,
                                                         receita_2020_1_role_repasse_nao_conferida,
                                                         receita_2020_1_ptrf_repasse_conferida,
                                                         receita_2020_1_role_repasse_cheque_conferida
                                                         ):
    prestacao_uuid = prestacao_conta_iniciada.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/receitas/?acao_associacao_uuid={acao_uuid}&conferido=False'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = []
    result_esperado = ReceitaListaSerializer(receita_2020_1_role_repasse_nao_conferida, many=False).data
    resultado_esperado.append(result_esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de receitas não conferidas."


def test_api_get_receitas_nao_conferidas_traz_periodos_anteriores(client,
                                                                  acao_associacao_role_cultural,
                                                                  prestacao_conta_iniciada,
                                                                  receita_2019_2_role_repasse_conferida,
                                                                  receita_2019_2_role_repasse_nao_conferida,
                                                                  receita_2020_1_role_repasse_conferida,
                                                                  receita_2020_1_role_repasse_nao_conferida,
                                                                  receita_2020_1_ptrf_repasse_conferida,
                                                                  receita_2020_1_role_repasse_cheque_conferida
                                                                  ):
    prestacao_uuid = prestacao_conta_iniciada.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/receitas/?acao_associacao_uuid={acao_uuid}&conferido=False'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = []
    result_esperado = ReceitaListaSerializer(receita_2019_2_role_repasse_nao_conferida, many=False).data
    resultado_esperado.append(result_esperado)

    result_esperado = ReceitaListaSerializer(receita_2020_1_role_repasse_nao_conferida, many=False).data
    resultado_esperado.append(result_esperado)


    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de receitas esperada. Deve incluir períodos anteriores"
