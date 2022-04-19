import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_acoes_demonstrativo_financeiro(jwt_authenticated_client_a, periodo, conta_associacao, associacao, conta_associacao_cheque, fechamento_periodo):
    url = f"/api/demonstrativo-financeiro/acoes/?associacao_uuid={associacao.uuid}&conta-associacao={conta_associacao.uuid}&periodo_uuid={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)
    result_cartao = response.json()

    url = f"/api/demonstrativo-financeiro/acoes/?associacao_uuid={associacao.uuid}&conta-associacao={conta_associacao_cheque.uuid}&periodo_uuid={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)
    result_cheque = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result_cartao != result_cheque
