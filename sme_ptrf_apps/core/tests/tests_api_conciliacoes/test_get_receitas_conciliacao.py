import json
from uuid import uuid4

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

from ....receitas.api.serializers import ReceitaListaSerializer

pytestmark = pytest.mark.django_db


def test_api_get_receitas_sem_periodo(jwt_authenticated_client_a, acao_associacao_role_cultural, conta_associacao_cartao):
    url = f'/api/conciliacoes/receitas/?conta_associacao={conta_associacao_cartao.uuid}&acao_associacao={acao_associacao_role_cultural.uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_get_receitas_periodo_nao_encontrado(jwt_authenticated_client_a, acao_associacao_role_cultural, conta_associacao_cartao):
    url = f'/api/conciliacoes/receitas/?periodo={uuid4()}&conta_associacao={conta_associacao_cartao.uuid}&acao_associacao={acao_associacao_role_cultural.uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_api_get_receitas_sem_conta_associacao(jwt_authenticated_client_a, acao_associacao_role_cultural, periodo_2020_1):
    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&acao_associacao={acao_associacao_role_cultural.uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_get_receitas_conta_associacao_nao_encontrada(jwt_authenticated_client_a, acao_associacao_role_cultural, periodo_2020_1):
    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&conta_associacao={uuid4()}&acao_associacao={acao_associacao_role_cultural.uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_api_get_receitas_sem_acao_associacao(jwt_authenticated_client_a, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_associacao_cartao.uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requerido'


def test_api_get_receitas_acao_associacao_nao_encontrada(jwt_authenticated_client_a, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_associacao_cartao.uuid}&acao_associacao={uuid4()}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_api_get_receitas_sem_conferido(jwt_authenticated_client_a, acao_associacao_role_cultural, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/receitas/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_associacao_cartao.uuid}&acao_associacao={acao_associacao_role_cultural.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requerido'


def test_api_get_receitas_conferidas(jwt_authenticated_client_a,
                                     acao_associacao_role_cultural,
                                     receita_2019_2_role_repasse_conferida,
                                     receita_2020_1_role_repasse_conferida,
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
    receitas_esperadas.add(f'{receita_2020_1_role_repasse_conferida.uuid}')

    assert response.status_code == status.HTTP_200_OK
    assert receitas_retornadas == receitas_esperadas, "Não retornou a lista de receitas esperada."


def test_api_get_receitas_nao_conferidas_prestacao_conta(jwt_authenticated_client_a,
                                                         acao_associacao_role_cultural,
                                                         receita_2019_2_role_repasse_conferida,
                                                         receita_2020_1_role_repasse_conferida,
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

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de receitas não conferidas."


def test_api_get_receitas_nao_conferidas_traz_periodos_anteriores(jwt_authenticated_client_a,
                                                                  acao_associacao_role_cultural,
                                                                  receita_2019_2_role_repasse_conferida,
                                                                  receita_2020_1_role_repasse_conferida,
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

    assert response.status_code == status.HTTP_200_OK
    assert receitas_retornadas == receitas_esperadas, "Não retornou a lista de receitas esperada. Deve incluir períodos anteriores"
