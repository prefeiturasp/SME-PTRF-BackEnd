import pytest

from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag("novo-processo-pc", active=False)
def test_concluir_v2_nao_pode_ser_executado_sem_feature_flag_ativa(
    jwt_authenticated_client_a,
):
    url = f"/api/prestacoes-contas/concluir-v2/"

    response = jwt_authenticated_client_a.post(
        url, content_type="application/json", data={}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@override_flag("novo-processo-pc", active=True)
def test_concluir_v2_dev_exigir_os_parametros(
    jwt_authenticated_client_a,
):
    url = f"/api/prestacoes-contas/concluir-v2/"

    response = jwt_authenticated_client_a.post(
        url, content_type="application/json", data={}
    )

    # Verificando se o status code é 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Verificando se as mensagens de erro indicam a falta dos parâmetros obrigatórios
    assert "associacao_uuid" in response.data
    assert "periodo_uuid" in response.data
