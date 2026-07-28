from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido


@dataclass
class BemProduzidoDtoContext:
    """Contexto imutável de entrada construído antes de executar o pipeline de validação do bem produzido."""

    # Operação
    is_create: bool

    # Objeto principal do fluxo
    bem_produzido: Optional["BemProduzido"] = None

    # Dados de domínio
    associacao: Any = None
    status: Optional[str] = None
    recurso: Optional[str] = None

    # Campos opcionais enriquecidos por validators intermediários
    periodos: Optional[list] = field(default=None)
    saldos: Optional[dict] = field(default=None)
    observacoes: Optional[str] = field(default=None)
