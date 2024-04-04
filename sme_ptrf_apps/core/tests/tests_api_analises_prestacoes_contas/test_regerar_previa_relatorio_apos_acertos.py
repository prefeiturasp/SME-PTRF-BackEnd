import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models.tasks_celery import TaskCelery

pytestmark = pytest.mark.django_db


def test_regerar_previa_relatorio_apos_acertos(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises_sem_versao,
    conta_associacao_cartao,
    conta_associacao_cheque
):

    analise_prestacao = analise_prestacao_conta_2020_1_teste_analises_sem_versao.uuid
    url = f'/api/analises-prestacoes-contas/regerar-previa-relatorio-apos-acertos/?analise_prestacao_uuid={analise_prestacao}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "mensagem": "Arquivo na fila para processamento."
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado == result
    assert TaskCelery.objects.filter(nome_task='regerar_previa_relatorio_apos_acertos_v2_async').exists()
