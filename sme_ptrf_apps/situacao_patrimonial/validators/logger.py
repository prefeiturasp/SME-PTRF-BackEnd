from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .context import BemProduzidoDtoContext

_DEFAULT_LOGGER = logging.getLogger("sme_ptrf_apps.situacao_patrimonial.validators")


class ContextualLogger(logging.LoggerAdapter):
    """LoggerAdapter que prefixa cada mensagem com o contexto do pipeline de validação.

    Carrega automaticamente: campos (se disponível)
    e associacao_uuid (se disponível). O validator atual é adicionado via `with_validator()`.

    Uso típico (dentro do ValidatorPipeline):

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1 — Criação")
        log.info("Pipeline iniciado")

        v_log = log.with_validator("RateiosObrigatoriosValidator")
        v_log.debug("Executando")

    Saída de exemplo:
        [flow=Fluxo 1 — Criação | is_create=True | is_acerto=False] Pipeline iniciado
        [flow=Fluxo 1 — Criação | ... | validator=RateiosObrigatoriosValidator] Executando
    """

    def process(self, msg: str, kwargs: dict) -> tuple:
        ctx_str = " | ".join(f"{k}={v}" for k, v in self.extra.items())
        return f"[{ctx_str}] {msg}", kwargs

    @classmethod
    def from_context(
        cls,
        ctx: "BemProduzidoDtoContext",
        flow_name: str,
        base_logger: Optional[logging.Logger] = None,
    ) -> "ContextualLogger":
        """Constrói o logger com campos derivados do BemProduzidoDtoContext."""
        _logger = base_logger or _DEFAULT_LOGGER

        extra: dict = {
            "flow": flow_name,
        }

        recurso = ctx.recurso
        if recurso is not None:
            extra["recurso_id"] = getattr(recurso, "id", str(recurso))

        if ctx.bem_produzido is not None:
            extra["bem_produzido_id"] = ctx.bem_produzido.id
            extra["bem_produzido_uuid"] = str(ctx.bem_produzido.uuid)

        if ctx.associacao is not None:
            extra["associacao_id"] = ctx.associacao.id
            extra["associacao_uuid"] = ctx.associacao.uuid

        operation_id = " | ".join(f"{k}={v}" for k, v in extra.items())
        extra["operation_id"] = operation_id
        return cls(_logger, extra)

    def with_validator(self, validator_name: str) -> "ContextualLogger":
        """Retorna um novo logger com o validator atual adicionado ao contexto."""
        return ContextualLogger(self.logger, {**self.extra, "validator": validator_name})
