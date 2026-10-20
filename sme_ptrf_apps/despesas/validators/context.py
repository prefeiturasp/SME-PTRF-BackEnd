from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Optional


@dataclass
class DespesaDtoContext:
    """Contexto imutável de entrada construído antes de executar o pipeline de validação.

    Validators intermediários podem enriquecer os campos opcionais `periodo` e `saldos`
    retornando o próprio ctx após atribuir os valores.

    Fluxos suportados:
        Fluxo 1 — Criação normal:           is_create=True,  uuid_solicitacao_acerto=None
        Fluxo 2 — Edição normal:            is_create=False, uuid_solicitacao_acerto=None
        Fluxo 3 — Criação via acerto:       is_create=True,  uuid_solicitacao_acerto=<uuid>
        Fluxo 4 — Edição via acerto:        is_create=False, uuid_solicitacao_acerto=<uuid>
    """

    # Operação
    is_create: bool

    # Dados normalizados de entrada
    valor_total: Decimal
    valor_recursos_proprios: Decimal
    data_transacao: Optional[date]
    data_documento: Optional[date]
    retem_imposto: bool
    eh_despesa_reconhecida_pela_associacao: bool
    numero_boletim_de_ocorrencia: str
    eh_despesa_sem_comprovacao_fiscal: bool
    tipo_documento: Any  # TipoDocumento | None
    tipo_transacao: Any  # TipoTransacao | None
    numero_documento: str
    documento_transacao: str
    cpf_cnpj_fornecedor: str
    nome_fornecedor: str

    # Rateios validados pelo DRF (FKs são instâncias de model)
    rateios: list
    # Rateios brutos do initial_data (FKs são UUID strings) — usados por serviços legados
    rateios_raw: list
    # Despesas de imposto validadas pelo DRF
    despesas_impostos: list

    # Pagamento antecipado
    motivos_pagamento_antecipado: list
    outros_motivos: Optional[str]

    # Objetos resolvidos
    associacao: Any   # Associacao | None
    recurso: Any      # Recurso | None  (None no update — vem de despesa_instance.recurso)
    despesa_instance: Any  # Despesa | None  (None no create)

    # Enriquecidos por validators intermediários
    periodo: Optional[Any] = field(default=None)      # Periodo — preenchido por v07
    saldos: Optional[dict] = field(default=None)      # preenchido por v13

    # Dados financeiros complementares
    # Valor exibido no extrato comprobatório; difere de valor_total quando há ajuste.
    valor_original: Optional[Decimal] = field(default=None)

    # Contexto de Solicitação de Acerto (fluxos 3 e 4)
    # UUID de SolicitacaoAcertoDocumento que originou a criação/edição da despesa.
    # Não-None indica que o fluxo vem de uma análise DRE com acerto de documento.
    uuid_solicitacao_acerto: Optional[str] = field(default=None)

    @property
    def is_acerto(self) -> bool:
        """True quando a operação é originada de uma Solicitação de Acerto (fluxos 3 e 4)."""
        return self.uuid_solicitacao_acerto is not None

    @property
    def recurso_efetivo(self) -> Any:
        """Retorna o recurso correto independente de create/update."""
        if self.recurso:
            return self.recurso
        if self.despesa_instance:
            return self.despesa_instance.recurso
        return None
