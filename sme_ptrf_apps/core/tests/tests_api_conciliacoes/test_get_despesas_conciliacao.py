import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_despesas_conferidas(jwt_authenticated_client_a,
                                     acao_associacao_role_cultural,
                                     despesa_2019_2,
                                     rateio_despesa_2019_role_conferido,
                                     rateio_despesa_2019_role_conferido_no_periodo,
                                     despesa_2020_1,
                                     rateio_despesa_2020_role_conferido,
                                     rateio_despesa_2020_role_nao_conferido,
                                     rateio_despesa_2020_ptrf_conferido,
                                     rateio_despesa_2020_role_cheque_conferido,
                                     periodo_2020_1,
                                     conta_associacao_cartao
                                     ):
    conta_uuid = conta_associacao_cartao.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/conciliacoes/despesas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&acao_associacao={acao_uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    despesas_retornadas = set()
    for despesa in result:
        despesas_retornadas.add(despesa['uuid'])

    despesas_esperadas = set()
    despesas_esperadas.add(f'{rateio_despesa_2020_role_conferido.uuid}')
    despesas_esperadas.add(f'{rateio_despesa_2019_role_conferido_no_periodo.uuid}')

    assert response.status_code == status.HTTP_200_OK
    assert despesas_retornadas == despesas_esperadas, "Não retornou a lista de despesas esperada."


def test_api_get_despesas_nao_conferidas_prestacao_conta(jwt_authenticated_client_a,
                                                         acao_associacao_role_cultural,
                                                         despesa_2019_2,
                                                         rateio_despesa_2019_role_conferido,
                                                         despesa_2020_1,
                                                         rateio_despesa_2020_role_conferido,
                                                         rateio_despesa_2020_role_nao_conferido,
                                                         rateio_despesa_2020_ptrf_conferido,
                                                         rateio_despesa_2020_role_cheque_conferido,
                                                         periodo_2020_1,
                                                         conta_associacao_cartao
                                                         ):
    conta_uuid = conta_associacao_cartao.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/conciliacoes/despesas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&acao_associacao={acao_uuid}&conferido=False'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    despesas_retornadas = set()
    for despesa in result:
        despesas_retornadas.add(despesa['uuid'])

    despesas_esperadas = set()
    despesas_esperadas.add(f'{rateio_despesa_2020_role_nao_conferido.uuid}')

    assert response.status_code == status.HTTP_200_OK
    assert despesas_retornadas == despesas_esperadas, "Não retornou a lista de despesas esperada."


def test_api_get_despesas_nao_conferidas_prestacao_traz_periodos_anteriores(jwt_authenticated_client_a,
                                                                            acao_associacao_role_cultural,
                                                                            despesa_2019_2,
                                                                            rateio_despesa_2019_role_conferido,
                                                                            rateio_despesa_2019_role_nao_conferido,
                                                                            despesa_2020_1,
                                                                            rateio_despesa_2020_role_conferido,
                                                                            rateio_despesa_2020_role_nao_conferido,
                                                                            rateio_despesa_2020_ptrf_conferido,
                                                                            rateio_despesa_2020_role_cheque_conferido,
                                                                            periodo_2020_1,
                                                                            conta_associacao_cartao
                                                                            ):
    conta_uuid = conta_associacao_cartao.uuid
    acao_uuid = acao_associacao_role_cultural.uuid

    url = f'/api/conciliacoes/despesas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&acao_associacao={acao_uuid}&conferido=False'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        f'{rateio_despesa_2020_role_nao_conferido.uuid}',
        f'{rateio_despesa_2019_role_nao_conferido.uuid}',

    }


    assert response.status_code == status.HTTP_200_OK

    for r in result:
        esperado.discard(r['uuid'])

    assert esperado == set(), "Não retornou a lista de despesas esperada."
