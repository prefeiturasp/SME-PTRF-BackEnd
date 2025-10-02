import pytest
from datetime import date
from unittest.mock import patch
from rest_framework import status
from waffle.testutils import override_flag
from sme_ptrf_apps.core.models import PrestacaoConta

pytestmark = pytest.mark.django_db


@override_flag("novo-processo-pc", active=False)
def test_concluir_v2_nao_pode_ser_executado_sem_feature_flag_ativa(
    jwt_authenticated_client_a,
):
    url = "/api/prestacoes-contas/concluir-v2/"

    response = jwt_authenticated_client_a.post(
        url, content_type="application/json", data={}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@override_flag("novo-processo-pc", active=True)
def test_concluir_v2_dev_exigir_os_parametros(
    jwt_authenticated_client_a,
):
    url = "/api/prestacoes-contas/concluir-v2/"

    response = jwt_authenticated_client_a.post(
        url, content_type="application/json", data={}
    )

    # Verificando se o status code é 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Verificando se as mensagens de erro indicam a falta dos parâmetros obrigatórios
    assert "associacao_uuid" in response.data
    assert "periodo_uuid" in response.data


@patch("sme_ptrf_apps.core.services.periodo_services.pc_tem_solicitacoes_de_acerto_pendentes", return_value=False)
@override_flag("novo-processo-pc", active=True)
def test_concluir_v2_sem_pc_existente_permite_fluxo(
    mock_acertos,
    jwt_authenticated_client_a,
    associacao_factory,
    periodo_factory,
):
    url = "/api/prestacoes-contas/concluir-v2/"
    associacao = associacao_factory()
    periodo = periodo_factory()

    payload = {
        "associacao_uuid": str(associacao.uuid),
        "periodo_uuid": str(periodo.uuid),
    }

    response = jwt_authenticated_client_a.post(url, format="json", data=payload)

    # Como não existe PC, o validate não deve bloquear. Ajuste o status conforme seu endpoint (200/201/etc.).
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}
    assert "non_field_errors" not in response.data


@patch("sme_ptrf_apps.core.services.periodo_services.pc_tem_solicitacoes_de_acerto_pendentes", return_value=False)
@override_flag("novo-processo-pc", active=True)
def test_concluir_v2_status_invalido_bloqueia(
    mock_acertos,
    jwt_authenticated_client_a,
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
):
    url = "/api/prestacoes-contas/concluir-v2/"
    associacao = associacao_factory()
    periodo = periodo_factory()
    # Cria PC com status NÃO permitido (ex.: qualquer um diferente de NAO_APRESENTADA/DEVOLVIDA)
    prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo,
        status=PrestacaoConta.STATUS_EM_ANALISE,
    )

    payload = {
        "associacao_uuid": str(associacao.uuid),
        "periodo_uuid": str(periodo.uuid),
    }

    response = jwt_authenticated_client_a.post(url, format="json", data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data
    assert "só pode ser concluída" in " ".join(response.data["non_field_errors"]).lower()


@patch("sme_ptrf_apps.core.services.periodo_services.pc_tem_solicitacoes_de_acerto_pendentes", return_value=False)
@override_flag("novo-processo-pc", active=True)
def test_concluir_v2_status_permitido_sem_acertos_pendentes_permite(
    mock_acertos,
    jwt_authenticated_client_a,
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
):
    url = "/api/prestacoes-contas/concluir-v2/"
    associacao = associacao_factory()
    periodo = periodo_factory()
    prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo,
        status=PrestacaoConta.STATUS_NAO_APRESENTADA,  # permitido
    )

    payload = {
        "associacao_uuid": str(associacao.uuid),
        "periodo_uuid": str(periodo.uuid),
    }

    response = jwt_authenticated_client_a.post(url, format="json", data=payload)

    assert response.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}
    assert "non_field_errors" not in response.data


@patch("sme_ptrf_apps.core.services.periodo_services.pc_tem_solicitacoes_de_acerto_pendentes", return_value=True)
@override_flag("novo-processo-pc", active=True)
def test_concluir_v2_status_permitido_com_acertos_pendentes_bloqueia(
    mock_acertos,
    jwt_authenticated_client_a,
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
):
    url = "/api/prestacoes-contas/concluir-v2/"
    associacao = associacao_factory()
    periodo = periodo_factory()
    prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo,
        status=PrestacaoConta.STATUS_DEVOLVIDA,  # permitido, mas com acertos pendentes deve bloquear
    )

    payload = {
        "associacao_uuid": str(associacao.uuid),
        "periodo_uuid": str(periodo.uuid),
    }

    response = jwt_authenticated_client_a.post(url, format="json", data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data
    assert "acerto" in " ".join(response.data["non_field_errors"]).lower()


@override_flag("novo-processo-pc", active=True)
def test_concluir_v2_com_saldo_alterado_sem_solicitacao(
    jwt_authenticated_client_a,
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
    conta_associacao_factory,
):
    url = "/api/prestacoes-contas/concluir-v2/"
    associacao = associacao_factory()
    periodo = periodo_factory()
    pc = prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo,
        status=PrestacaoConta.STATUS_DEVOLVIDA,
        data_recebimento=periodo.data_inicio_realizacao_despesas
    )
    conta = conta_associacao_factory(associacao=associacao, data_inicio=date(2019, 2, 2))

    payload = {
        "associacao_uuid": str(associacao.uuid),
        "periodo_uuid": str(periodo.uuid),
    }

    with patch.object(
        pc.__class__,
        "contas_saldos_alterados_sem_solicitacao",
        return_value=[conta]
    ):
        response = jwt_authenticated_client_a.post(url, format="json", data=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "erro" in response.data
        assert response.data["erro"] == ["prestacao_com_saldos_alterados_sem_solicitacao"]

        assert "mensagem" in response.data
        assert "O saldo bancário" in response.data["mensagem"][0]
