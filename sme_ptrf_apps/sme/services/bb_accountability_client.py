import logging
import re
import time
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from typing import Optional
from django.conf import settings

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

HTTP_400_CONTA_NAO_DISPONIVEL = object()

# ──────────────────────────────────────────────────────────────────────────────
# Configurações (definir no .env e referenciar no settings.py)
#
# BB_CLIENT_ID=seu_client_id
# BB_CLIENT_SECRET=seu_client_secret
# BB_APP_KEY=seu_aap_key
# BB_OAUTH_URL=https://api.example.com/oauth/token
# BB_API_BASE_URL=https://api.example.com
# ──────────────────────────────────────────────────────────────────────────────

# Rate limiting: 25 TPS com margem de segurança
_TPS_LIMIT = 25
_TPS_INTERVAL = 1.0 / _TPS_LIMIT  # ~0.04 s entre chamadas
_TPS_BACKOFF_INICIAL = 1.0  # espera inicial após 429 (segundos)
_MAX_RETRIES = 2  # tentativas máximas por conta
_TOKEN_MARGEM_SEGUNDOS = 30  # renova token 30 s antes de expirar


class BBTokenManager:
    """
    Gerencia o ciclo de vida do access_token do Banco do Brasil.

    - Gera o token na primeira chamada.
    - Reutiliza enquanto não expirou (com margem de _TOKEN_MARGEM_SEGUNDOS).
    - Renova automaticamente quando expirado ou quando a API retorna 401.
    """

    def __init__(self):
        self._token: Optional[str] = None
        self._expira_em: Optional[datetime] = None

    # ── Credenciais ──────────────────────────────────────────────────────────

    @staticmethod
    def _basic_credentials() -> str:
        """Retorna o header Basic com as credenciais em Base64."""
        BB_CLIENT_ID = settings.BB_CLIENT_ID
        BB_CLIENT_SECRET = settings.BB_CLIENT_SECRET
        raw = f"{BB_CLIENT_ID}:{BB_CLIENT_SECRET}"
        return b64encode(raw.encode()).decode()

    # ── Token ─────────────────────────────────────────────────────────────────

    def _token_valido(self) -> bool:
        if not self._token or not self._expira_em:
            return False
        return datetime.now(timezone.utc) < (
            self._expira_em - timedelta(seconds=_TOKEN_MARGEM_SEGUNDOS)
        )

    def _gerar_token(self) -> str:
        """Faz a chamada OAuth e armazena o token retornado."""
        logger.info("[BB] Gerando novo access_token...")

        BB_OAUTH_URL = settings.BB_OAUTH_URL

        headers = {
            "Authorization": f"Basic {self._basic_credentials()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = {
            "grant_type": "client_credentials",
            "scope": "accountability.statements",
        }
        resp = requests.post(BB_OAUTH_URL, headers=headers, data=body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        expires_in = int(data.get("expires_in", 600))
        self._expira_em = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        logger.info(f"[BB] Token gerado. Expira em {expires_in}s.")
        return self._token

    def get_token(self, forcar_renovacao: bool = False) -> str:
        """Retorna token válido, renovando se necessário."""
        if forcar_renovacao or not self._token_valido():
            return self._gerar_token()
        return self._token


class BBAccountabilityClient:
    """
    Cliente para a API Accountability do Banco do Brasil.

    Funcionalidades:
    - Controle automático de TPS (25 requisições/segundo).
    - Renovação automática de token (validade de 10 minutos).
    - Retry com back-off em caso de 429 (TPS excedido) ou 401 (token expirado).
    - Máximo de 3 tentativas por chamada; em caso de falha retorna None.
    """

    def __init__(self):
        self._token_manager = BBTokenManager()
        self._ultimo_request_ts: float = 0.0  # timestamp da última chamada

    # ── Rate limiting ─────────────────────────────────────────────────────────

    def _aguardar_tps(self):
        """Garante espaçamento mínimo entre chamadas para não exceder 25 TPS."""
        agora = time.monotonic()
        decorrido = agora - self._ultimo_request_ts
        if decorrido < _TPS_INTERVAL:
            time.sleep(_TPS_INTERVAL - decorrido)
        self._ultimo_request_ts = time.monotonic()

    # ── Formatação de agência/conta ───────────────────────────────────────────

    @staticmethod
    def formatar_agencia(agencia: str) -> str:
        """
        Remove o DV da agência apenas quando ele está explicitamente presente.

        Regras:
        - Com hífen separador → remove o DV: "2801-X" → "2801", "2801-7" → "2801"
        - Com DV letra sem hífen → remove: "2801X" → "2801"
        - Número puro → mantém intacto: "2801" → "2801", "4752" → "4752"
        """
        agencia = str(agencia).strip()

        # Caso 1: contém hífen → tudo antes do hífen é o número da agência
        if "-" in agencia:
            return agencia.split("-")[0].strip()

        # Caso 2: termina com letra (X/x) sem hífen → remove apenas a letra
        if agencia and agencia[-1].upper() == "X":
            return agencia[:-1].strip()

        # Caso 3: número puro → retorna sem alteração
        return agencia

    @staticmethod
    def formatar_conta(numero_conta: str) -> str:
        """
        Remove o DV da conta (apenas quando explicitamente presente) e zeros à esquerda.

        Regras:
        - Com hífen separador → remove o DV: "97935-X" → "97935", "97935-8" → "97935"
        - Com DV letra sem hífen → remove: "97935X" → "97935"
        - Número puro (com ou sem zeros à esquerda) → mantém só os dígitos sem zeros:
          "000097935" → "97935", "46539" → "46539"
        """
        numero_conta = str(numero_conta).strip()

        # Caso 1: contém hífen → tudo antes do hífen é o número da conta
        if "-" in numero_conta:
            numero_conta = numero_conta.split("-")[0].strip()

        # Caso 2: termina com letra (X/x) sem hífen → remove apenas a letra
        elif numero_conta and numero_conta[-1].upper() == "X":
            numero_conta = numero_conta[:-1].strip()

        # Remove zeros à esquerda (mantém "0" se o número for zero)
        return numero_conta.lstrip("0") or "0"

    def formatar_agencia_conta(self, agencia: str, numero_conta: str) -> str:
        """Retorna o formato esperado pela API: 'agencia-conta' (ex: '2801-97935')."""
        return f"{self.formatar_agencia(agencia)}-{self.formatar_conta(numero_conta)}"

    # ── Chamada HTTP com retry ────────────────────────────────────────────────

    def _get(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        """
        Executa GET na API com:
        - Controle de TPS
        - Retry em 401 (renova token) e 429 (back-off + retry)
        - Máximo de _MAX_RETRIES tentativas
        - Retorna None após esgotar tentativas (não aborta o fluxo)
        """

        BB_APP_KEY = settings.BB_APP_KEY
        BB_API_BASE_URL = settings.BB_API_BASE_URL

        params = params or {}
        params["gw-app-key"] = BB_APP_KEY
        backoff = _TPS_BACKOFF_INICIAL


        for tentativa in range(1, _MAX_RETRIES + 1):
            self._aguardar_tps()
            token = self._token_manager.get_token()
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BB_API_BASE_URL}{path}"

            try:
                resp = requests.get(url, headers=headers, params=params, timeout=15)
            except requests.exceptions.RequestException as exc:
                logger.warning(
                    f"[BB] Tentativa {tentativa}/{_MAX_RETRIES} — erro de conexão: {exc}"
                )
                if tentativa < _MAX_RETRIES:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                return None

            # ── 401: token expirado → renova e repete ───────────────────────
            if resp.status_code == 401:
                logger.warning(
                    f"[BB] Tentativa {tentativa}/{_MAX_RETRIES} — 401, renovando token..."
                )
                self._token_manager.get_token(forcar_renovacao=True)
                if tentativa < _MAX_RETRIES:
                    continue
                return None

            # ── 429: TPS excedido → back-off e repete ───────────────────────
            if resp.status_code == 429:
                logger.warning(
                    f"[BB] Tentativa {tentativa}/{_MAX_RETRIES} — 429 (TPS), aguardando {backoff}s..."
                )
                time.sleep(backoff)
                backoff *= 2
                continue

            if resp.status_code == 400:
                logger.warning(
                    f"[BB] HTTP 400 ao consultar {path}: {resp.text[:300]}"
                )
                return HTTP_400_CONTA_NAO_DISPONIVEL

            # ── Outros erros HTTP ────────────────────────────────────────────
            if not resp.ok:
                logger.error(
                    f"[BB] Tentativa {tentativa}/{_MAX_RETRIES} — HTTP {resp.status_code}: {resp.text[:300]}"
                )
                if tentativa < _MAX_RETRIES:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                return None

            return resp.json()

        return None

    # ── Endpoints de saldo ────────────────────────────────────────────────────

    _SALDO_INDISPONIVEL = "Saldo indisponível"

    @staticmethod
    def _extrair_valor_disponibilidade(
        data: dict, agencia_conta: str, endpoint: str
    ) -> Optional[float]:
        """
        Extrai o campo 'valorDisponibilidade' de uma resposta da API.

        Retorna o valor como float, ou None se ausente/inválido.
        Estrutura esperada: { "dataSaldo": "DD/MM/AAAA", "valorDisponibilidade": 0.00, ... }
        """
        if "valorDisponibilidade" not in data:
            logger.warning(
                f"[BB] Campo 'valorDisponibilidade' ausente na resposta de {endpoint} "
                f"para {agencia_conta}: {data}"
            )
            return None
        try:
            return float(data["valorDisponibilidade"])
        except (ValueError, TypeError) as exc:
            logger.exception(
                f"[BB] Erro ao converter 'valorDisponibilidade' de {endpoint} "
                f"para {agencia_conta}: {exc} | data={data}"
            )
            return None

    def _obter_saldo_conta_corrente(self, agencia_conta: str) -> Optional[float]:
        """
        GET /saldos/{agencia}-{conta}/conta-corrente

        Retorna o valorDisponibilidade como float, ou None em caso de falha.
        Resposta esperada: { "dataSaldo": "DD/MM/AAAA", "valorDisponibilidade": 0.00 }
        """
        path = f"/saldos/{agencia_conta}/conta-corrente"
        logger.info(f"[BB] Consultando saldo conta corrente de {agencia_conta}...")
        data = self._get(path)

        if data is None:
            logger.error(
                f"[BB] Falha ao obter saldo conta corrente de {agencia_conta} "
                f"após {_MAX_RETRIES} tentativas."
            )
            return None

        if data is HTTP_400_CONTA_NAO_DISPONIVEL:
            logger.warning(
                f"[BB] Saldo conta corrente não disponível para {agencia_conta} por HTTP 400."
            )
            return HTTP_400_CONTA_NAO_DISPONIVEL

        return self._extrair_valor_disponibilidade(
            data, agencia_conta, "conta-corrente"
        )

    def _obter_saldo_aplicacoes_financeiras(
        self, agencia_conta: str
    ) -> Optional[float]:
        """
        GET /saldos/{agencia}-{conta}/aplicacoes-financeiras

        Retorna o valorDisponibilidade como float, ou None em caso de falha.
        Resposta esperada:
        {
            "dataSaldo": "DD/MM/AAAA",
            "valorDisponibilidade": 0.00,
            "indicadorSaldoNaoDisponivel": "S" ou "N",  ← ignorado
            "operacoes": [ ... ]
        }
        O campo indicadorSaldoNaoDisponivel é ignorado — o valorDisponibilidade
        sempre traz o valor correto independentemente dele.
        """
        path = f"/saldos/{agencia_conta}/aplicacoes-financeiras"
        logger.info(
            f"[BB] Consultando saldo aplicações financeiras de {agencia_conta}..."
        )
        data = self._get(path)

        if data is None:
            logger.error(
                f"[BB] Falha ao obter saldo aplicações financeiras de {agencia_conta} "
                f"após {_MAX_RETRIES} tentativas."
            )
            return None

        if data is HTTP_400_CONTA_NAO_DISPONIVEL:
            logger.warning(
                f"[BB] Saldo aplicações financeiras não disponível para {agencia_conta} por HTTP 400."
            )
            return HTTP_400_CONTA_NAO_DISPONIVEL

        return self._extrair_valor_disponibilidade(
            data, agencia_conta, "aplicacoes-financeiras"
        )

    def obter_saldo_total(self, agencia: str, numero_conta: str) -> str:
        """
        Compõe o saldo real da conta somando dois endpoints:

            Saldo total = saldo conta corrente (valorDisponibilidade)
                        + saldo aplicações financeiras (valorDisponibilidade)

        Retorna o total formatado no padrão BR (ex: "1.234,56"), ou
        "Saldo indisponível" se qualquer uma das chamadas falhar ou
        indicar indisponibilidade.
        """
        agencia_conta = self.formatar_agencia_conta(agencia, numero_conta)

        saldo_cc = self._obter_saldo_conta_corrente(agencia_conta)
        if saldo_cc is HTTP_400_CONTA_NAO_DISPONIVEL:
            logger.warning(
                f"[BB] Saldo conta corrente retornou HTTP 400 para {agencia_conta}."
            )
            return "-"

        if saldo_cc is None:
            logger.error(
                f"[BB] Saldo conta corrente indisponível para {agencia_conta}."
            )
            return self._SALDO_INDISPONIVEL

        saldo_aplic = self._obter_saldo_aplicacoes_financeiras(agencia_conta)
        if saldo_aplic is HTTP_400_CONTA_NAO_DISPONIVEL:
            logger.warning(
                f"[BB] Saldo aplicações financeiras retornou HTTP 400 para {agencia_conta}."
            )
            return "-"

        if saldo_aplic is None:
            logger.error(
                f"[BB] Saldo aplicações financeiras indisponível para {agencia_conta}."
            )
            return self._SALDO_INDISPONIVEL

        saldo_total = saldo_cc + saldo_aplic
        logger.info(
            f"[BB] Saldo total de {agencia_conta}: "
            f"CC={saldo_cc} + Aplic={saldo_aplic} = {saldo_total}"
        )

        # 1.4 — Formato monetário padrão brasileiro: R$ 0.000,00
        valor_formatado = (
            f"{saldo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        return f"R$ {valor_formatado}"
