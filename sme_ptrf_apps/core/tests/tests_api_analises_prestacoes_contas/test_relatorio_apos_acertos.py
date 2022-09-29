import json
import pytest
from rest_framework import status
pytestmark = pytest.mark.django_db


def test_api_gerar_previa_pdf_apos_acertos(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises_sem_versao,
    conta_associacao_cartao,
    conta_associacao_cheque
):

    analise_prestacao = analise_prestacao_conta_2020_1_teste_analises_sem_versao.uuid
    url = f'/api/analises-prestacoes-contas/previa-relatorio-apos-acertos/?analise_prestacao_uuid={analise_prestacao}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
      "mensagem": "Arquivo na fila para processamento."
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado == result


def test_api_gerar_previa_pdf_apos_acertos_sem_analise_uuid(
    jwt_authenticated_client_a,
    conta_associacao_cartao,
    conta_associacao_cheque
):

    url = f'/api/analises-prestacoes-contas/previa-relatorio-apos-acertos/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_get_status_documento_apos_acertos(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises_com_versao_rascunho_em_processamento,
):
    analise_prestacao = analise_prestacao_conta_2020_1_teste_analises_com_versao_rascunho_em_processamento

    url = f'/api/analises-prestacoes-contas/status-info_relatorio_apos_acertos/?analise_prestacao_uuid={analise_prestacao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_api_get_status_documento_sem_documento(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises_sem_versao,
):
    analise_prestacao = analise_prestacao_conta_2020_1_teste_analises_sem_versao

    url = f'/api/analises-prestacoes-contas/status-info_relatorio_apos_acertos/?analise_prestacao_uuid={analise_prestacao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)
    resultado_esperado = "Nenhuma prévia gerada."

    assert resultado_esperado == result
    assert response.status_code == status.HTTP_200_OK
