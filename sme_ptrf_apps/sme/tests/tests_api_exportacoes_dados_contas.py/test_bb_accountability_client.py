from base64 import b64encode
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
import requests

from sme_ptrf_apps.sme.services import bb_accountability_client as bb_module
from sme_ptrf_apps.sme.services.bb_accountability_client import (
    BBAccountabilityClient,
    BBTokenManager,
    HTTP_400_CONTA_NAO_DISPONIVEL,
)


class FakeResponse:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text
        self.ok = 200 <= status_code < 400

    def json(self):
        return self._data

    def raise_for_status(self):
        if not self.ok:
            raise requests.exceptions.HTTPError(self.text)


@pytest.mark.parametrize(
    "agencia,esperado",
    [
        ("2801-X", "2801"),
        ("2801-7", "2801"),
        ("2801X", "2801"),
        ("2801x", "2801"),
        ("2801", "2801"),
        (" 4752 ", "4752"),
    ],
)
def test_formatar_agencia(agencia, esperado):
    assert BBAccountabilityClient.formatar_agencia(agencia) == esperado


@pytest.mark.parametrize(
    "numero_conta,esperado",
    [
        ("97935-X", "97935"),
        ("97935-8", "97935"),
        ("97935X", "97935"),
        ("97935x", "97935"),
        ("000097935", "97935"),
        ("46539", "46539"),
        ("0000", "0"),
    ],
)
def test_formatar_conta(numero_conta, esperado):
    assert BBAccountabilityClient.formatar_conta(numero_conta) == esperado


def test_formatar_agencia_conta():
    client = BBAccountabilityClient()

    assert client.formatar_agencia_conta("2801-X", "000097935-X") == "2801-97935"


def test_basic_credentials(monkeypatch):
    monkeypatch.setattr(bb_module.settings, "BB_CLIENT_ID", "client-id")
    monkeypatch.setattr(bb_module.settings, "BB_CLIENT_SECRET", "client-secret")

    esperado = b64encode("client-id:client-secret".encode()).decode()

    assert BBTokenManager._basic_credentials() == esperado


def test_token_valido_quando_token_existe_e_nao_expirou():
    token_manager = BBTokenManager()
    token_manager._token = "access-token"
    token_manager._expira_em = datetime.now(timezone.utc) + timedelta(minutes=5)

    assert token_manager._token_valido() is True


def test_token_invalido_quando_expirado():
    token_manager = BBTokenManager()
    token_manager._token = "access-token"
    token_manager._expira_em = datetime.now(timezone.utc) - timedelta(minutes=1)

    assert token_manager._token_valido() is False


def test_gerar_token_chama_oauth_e_armazena_token(monkeypatch):
    monkeypatch.setattr(bb_module.settings, "BB_OAUTH_URL", "https://oauth.example/token")
    monkeypatch.setattr(bb_module.settings, "BB_CLIENT_ID", "client-id")
    monkeypatch.setattr(bb_module.settings, "BB_CLIENT_SECRET", "client-secret")

    post_mock = Mock(
        return_value=FakeResponse(
            data={
                "access_token": "novo-token",
                "expires_in": 600,
            }
        )
    )
    monkeypatch.setattr(bb_module.requests, "post", post_mock)

    token_manager = BBTokenManager()

    assert token_manager._gerar_token() == "novo-token"
    assert token_manager._token == "novo-token"
    assert token_manager._expira_em is not None
    post_mock.assert_called_once_with(
        "https://oauth.example/token",
        headers={
            "Authorization": f"Basic {b64encode('client-id:client-secret'.encode()).decode()}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "client_credentials",
            "scope": "accountability.statements",
        },
        timeout=15,
    )


def test_get_com_sucesso_inclui_app_key_e_authorization(monkeypatch):
    monkeypatch.setattr(bb_module.settings, "BB_API_BASE_URL", "https://api.example")
    monkeypatch.setattr(bb_module.settings, "BB_APP_KEY", "app-key")

    client = BBAccountabilityClient()
    client._aguardar_tps = Mock()
    client._token_manager.get_token = Mock(return_value="access-token")

    get_mock = Mock(return_value=FakeResponse(data={"valorDisponibilidade": 10.25}))
    monkeypatch.setattr(bb_module.requests, "get", get_mock)

    resultado = client._get("/saldos/2801-97935/conta-corrente")

    assert resultado == {"valorDisponibilidade": 10.25}
    get_mock.assert_called_once_with(
        "https://api.example/saldos/2801-97935/conta-corrente",
        headers={"Authorization": "Bearer access-token"},
        params={"gw-app-key": "app-key"},
        timeout=15,
    )


def test_get_renova_token_apos_401_e_reexecuta(monkeypatch):
    monkeypatch.setattr(bb_module.settings, "BB_API_BASE_URL", "https://api.example")
    monkeypatch.setattr(bb_module.settings, "BB_APP_KEY", "app-key")
    monkeypatch.setattr(bb_module, "_MAX_RETRIES", 2)

    client = BBAccountabilityClient()
    client._aguardar_tps = Mock()

    chamadas_token = []

    def get_token(forcar_renovacao=False):
        chamadas_token.append(forcar_renovacao)
        return "access-token"

    client._token_manager.get_token = get_token

    get_mock = Mock(
        side_effect=[
            FakeResponse(status_code=401, text="unauthorized"),
            FakeResponse(data={"ok": True}),
        ]
    )
    monkeypatch.setattr(bb_module.requests, "get", get_mock)

    assert client._get("/saldos/2801-97935/conta-corrente") == {"ok": True}
    assert chamadas_token == [False, True, False]
    assert get_mock.call_count == 2


def test_get_retorna_none_apos_erro_de_conexao(monkeypatch):
    monkeypatch.setattr(bb_module, "_MAX_RETRIES", 1)

    client = BBAccountabilityClient()
    client._aguardar_tps = Mock()
    client._token_manager.get_token = Mock(return_value="access-token")

    monkeypatch.setattr(
        bb_module.requests,
        "get",
        Mock(side_effect=requests.exceptions.RequestException("falha de rede")),
    )

    assert client._get("/saldos/2801-97935/conta-corrente") is None


def test_get_retorna_none_apos_erro_http(monkeypatch):
    monkeypatch.setattr(bb_module, "_MAX_RETRIES", 1)

    client = BBAccountabilityClient()
    client._aguardar_tps = Mock()
    client._token_manager.get_token = Mock(return_value="access-token")

    monkeypatch.setattr(
        bb_module.requests,
        "get",
        Mock(return_value=FakeResponse(status_code=500, text="erro interno")),
    )

    assert client._get("/saldos/2801-97935/conta-corrente") is None


def test_get_retorna_http_400_conta_nao_disponivel(monkeypatch):
    monkeypatch.setattr(bb_module.settings, "BB_API_BASE_URL", "https://api.example")
    monkeypatch.setattr(bb_module.settings, "BB_APP_KEY", "app-key")

    client = BBAccountabilityClient()
    client._aguardar_tps = Mock()
    client._token_manager.get_token = Mock(return_value="access-token")

    monkeypatch.setattr(
        bb_module.requests,
        "get",
        Mock(return_value=FakeResponse(status_code=400, text="conta invalida")),
    )

    resultado = client._get("/saldos/2801-97935/conta-corrente")

    assert resultado is HTTP_400_CONTA_NAO_DISPONIVEL


def test_extrair_valor_disponibilidade_com_sucesso():
    resultado = BBAccountabilityClient._extrair_valor_disponibilidade(
        {"valorDisponibilidade": "123.45"},
        "2801-97935",
        "conta-corrente",
    )

    assert resultado == 123.45


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"valorDisponibilidade": "valor-invalido"},
        {"valorDisponibilidade": None},
    ],
)
def test_extrair_valor_disponibilidade_retorna_none_quando_invalido(data):
    resultado = BBAccountabilityClient._extrair_valor_disponibilidade(
        data,
        "2801-97935",
        "conta-corrente",
    )

    assert resultado is None


def test_obter_saldo_conta_corrente_usa_endpoint_e_extrai_valor():
    client = BBAccountabilityClient()
    client._get = Mock(return_value={"valorDisponibilidade": 50.15})

    assert client._obter_saldo_conta_corrente("2801-97935") == 50.15
    client._get.assert_called_once_with("/saldos/2801-97935/conta-corrente")


def test_obter_saldo_aplicacoes_financeiras_usa_endpoint_e_extrai_valor():
    client = BBAccountabilityClient()
    client._get = Mock(return_value={"valorDisponibilidade": 20.35})

    assert client._obter_saldo_aplicacoes_financeiras("2801-97935") == 20.35
    client._get.assert_called_once_with("/saldos/2801-97935/aplicacoes-financeiras")


def test_obter_saldo_conta_corrente_propaga_http_400():
    client = BBAccountabilityClient()
    client._get = Mock(return_value=HTTP_400_CONTA_NAO_DISPONIVEL)

    resultado = client._obter_saldo_conta_corrente("2801-97935")

    assert resultado is HTTP_400_CONTA_NAO_DISPONIVEL
    client._get.assert_called_once_with("/saldos/2801-97935/conta-corrente")


def test_obter_saldo_aplicacoes_financeiras_propaga_http_400():
    client = BBAccountabilityClient()
    client._get = Mock(return_value=HTTP_400_CONTA_NAO_DISPONIVEL)

    resultado = client._obter_saldo_aplicacoes_financeiras("2801-97935")

    assert resultado is HTTP_400_CONTA_NAO_DISPONIVEL
    client._get.assert_called_once_with("/saldos/2801-97935/aplicacoes-financeiras")


def test_obter_saldo_total_soma_endpoints_e_formata_valor():
    client = BBAccountabilityClient()
    client._obter_saldo_conta_corrente = Mock(return_value=1234.56)
    client._obter_saldo_aplicacoes_financeiras = Mock(return_value=10)

    resultado = client.obter_saldo_total("2801-X", "000097935-X")

    assert resultado == "R$ 1.244,56"
    client._obter_saldo_conta_corrente.assert_called_once_with("2801-97935")
    client._obter_saldo_aplicacoes_financeiras.assert_called_once_with("2801-97935")


@pytest.mark.parametrize(
    "saldo_cc,saldo_aplic",
    [
        (None, 10),
        (10, None),
    ],
)
def test_obter_saldo_total_retorna_indisponivel_quando_endpoint_falha(
    saldo_cc,
    saldo_aplic,
):
    client = BBAccountabilityClient()
    client._obter_saldo_conta_corrente = Mock(return_value=saldo_cc)
    client._obter_saldo_aplicacoes_financeiras = Mock(return_value=saldo_aplic)

    resultado = client.obter_saldo_total("2801", "97935")

    assert resultado == "Saldo indisponível"


@pytest.mark.parametrize(
    "saldo_cc,saldo_aplic",
    [
        (HTTP_400_CONTA_NAO_DISPONIVEL, 10),
        (10, HTTP_400_CONTA_NAO_DISPONIVEL),
    ],
)
def test_obter_saldo_total_retorna_hifen_quando_endpoint_retorna_http_400(
    saldo_cc,
    saldo_aplic,
):
    client = BBAccountabilityClient()
    client._obter_saldo_conta_corrente = Mock(return_value=saldo_cc)
    client._obter_saldo_aplicacoes_financeiras = Mock(return_value=saldo_aplic)

    resultado = client.obter_saldo_total("2801", "97935")

    assert resultado == "-"
