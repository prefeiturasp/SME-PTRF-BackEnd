import json

import pytest
from django.db.models import Q
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db(transaction=True)


# TODO: Débito técnico. Rever devido a erro com o Celery 5.1.2
# @pytest.mark.usefixtures('celery_session_app')
# @pytest.mark.usefixtures('celery_session_worker')
# def test_api_conclui_prestacao_conta(jwt_authenticated_client_a, associacao, periodo):
#     associacao_uuid = associacao.uuid
#     periodo_uuid = periodo.uuid
#
#     url = f'/api/prestacoes-contas/concluir/?associacao_uuid={associacao_uuid}&periodo_uuid={periodo_uuid}'
#
#     response = jwt_authenticated_client_a.post(url, content_type='application/json')
#
#     result = json.loads(response.content)
#
#     result_esperado = PrestacaoContaLookUpSerializer(
#         PrestacaoConta.objects.get(Q(associacao__uuid=associacao_uuid), Q(periodo__uuid=periodo_uuid)),
#         many=False).data
#
#     # Converto os campos UUIDs em strings para que a comparação funcione
#     result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'
#
#     assert response.status_code == status.HTTP_200_OK
#     assert result == result_esperado, "Não retornou a prestação de contas esperada."


# TODO: Débito técnico. Rever devido a erro com o Celery 5.1.2
# @pytest.mark.usefixtures('celery_session_app')
# @pytest.mark.usefixtures('celery_session_worker')
# def test_api_conclui_prestacao_conta_sem_periodo(jwt_authenticated_client_a, periodo, associacao):
#     associacao_uuid = associacao.uuid
#
#     url = f'/api/prestacoes-contas/concluir/?associacao_uuid={associacao_uuid}'
#
#     response = jwt_authenticated_client_a.post(url, content_type='application/json')
#
#     result = json.loads(response.content)
#
#     result_esperado = {
#         'erro': 'parametros_requeridos',
#         'mensagem': 'É necessário enviar o uuid do período de conciliação.'
#     }
#
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert result == result_esperado


# TODO: Débito técnico. Rever devido a erro com o Celery 5.1.2
# @pytest.mark.usefixtures('celery_session_app')
# @pytest.mark.usefixtures('celery_session_worker')
# def test_api_conclui_prestacao_conta_sem_associacao(jwt_authenticated_client_a, periodo, associacao):
#     periodo_uuid = periodo.uuid
#
#     url = f'/api/prestacoes-contas/concluir/?periodo_uuid={periodo_uuid}'
#
#     response = jwt_authenticated_client_a.post(url, content_type='application/json')
#
#     result = json.loads(response.content)
#
#     result_esperado = {
#         'erro': 'parametros_requeridos',
#         'mensagem': 'É necessário enviar o uuid da associação.'
#     }
#
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert result == result_esperado

