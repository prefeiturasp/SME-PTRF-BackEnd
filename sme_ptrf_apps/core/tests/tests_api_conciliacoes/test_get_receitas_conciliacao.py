import json

import pytest
from rest_framework import status

from ....receitas.api.serializers import ReceitaListaSerializer

pytestmark = pytest.mark.django_db


def test_api_get_receitas_conferidas(jwt_authenticated_client_a,
                                     acao_associacao_role_cultural,
                                     receita_2019_2_role_repasse_conferida,
                                     receita_2019_2_role_repasse_conferida_no_periodo,
                                     receita_2020_1_role_repasse_conferida,
                                     receita_2020_1_role_repasse_nao_conferida,
                                     receita_2020_1_ptrf_repasse_conferida,
                                     receita_2020_1_role_repasse_cheque_conferida,
                                     periodo_2020_1,
                                     conta_associacao_cartao
                                     ):
    conta_uuid = conta_associacao_cartao.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&acao_associacao={acao_uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    receitas_retornadas = set()
    for receita in result:
        receitas_retornadas.add(receita['uuid'])

    receitas_esperadas = set()
    receitas_esperadas.add(f'{receita_2019_2_role_repasse_conferida_no_periodo.uuid}')
    receitas_esperadas.add(f'{receita_2020_1_role_repasse_conferida.uuid}')

    assert response.status_code == status.HTTP_200_OK
    assert receitas_retornadas == receitas_esperadas, "Não retornou a lista de receitas esperada."


def test_api_get_receitas_nao_conferidas_prestacao_conta(jwt_authenticated_client_a,
                                                         acao_associacao_role_cultural,
                                                         receita_2019_2_role_repasse_conferida,
                                                         receita_2020_1_role_repasse_conferida,
                                                         receita_2020_1_role_repasse_nao_conferida,
                                                         receita_2020_1_ptrf_repasse_conferida,
                                                         receita_2020_1_role_repasse_cheque_conferida,
                                                         periodo_2020_1,
                                                         conta_associacao_cartao
                                                         ):
    conta_uuid = conta_associacao_cartao.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&acao_associacao={acao_uuid}&conferido=False'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = []
    result_esperado = ReceitaListaSerializer(receita_2020_1_role_repasse_nao_conferida, many=False).data
    resultado_esperado.append(result_esperado)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de receitas não conferidas."


def test_api_get_receitas_nao_conferidas_traz_periodos_anteriores(jwt_authenticated_client_a,
                                                                  acao_associacao_role_cultural,
                                                                  receita_2019_2_role_repasse_conferida,
                                                                  receita_2019_2_role_repasse_nao_conferida,
                                                                  receita_2020_1_role_repasse_conferida,
                                                                  receita_2020_1_role_repasse_nao_conferida,
                                                                  receita_2020_1_ptrf_repasse_conferida,
                                                                  receita_2020_1_role_repasse_cheque_conferida,
                                                                  periodo_2020_1,
                                                                  conta_associacao_cartao
                                                                  ):
    conta_uuid = conta_associacao_cartao.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&acao_associacao={acao_uuid}&conferido=False'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    receitas_retornadas = set()
    for receita in result:
        receitas_retornadas.add(receita['uuid'])

    receitas_esperadas = set()
    receitas_esperadas.add(f'{receita_2019_2_role_repasse_nao_conferida.uuid}')
    receitas_esperadas.add(f'{receita_2020_1_role_repasse_nao_conferida.uuid}')

    assert response.status_code == status.HTTP_200_OK
    assert receitas_retornadas == receitas_esperadas, "Não retornou a lista de receitas esperada. Deve incluir períodos anteriores"
