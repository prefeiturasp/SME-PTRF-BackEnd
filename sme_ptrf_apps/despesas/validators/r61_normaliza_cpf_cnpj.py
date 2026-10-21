from sme_ptrf_apps.core.models.validators import normalize_cpf_cnpj

from .base import AbstractDespesaValidator
from .context import DespesaDtoContext


class NormalizaCpfCnpjValidator(AbstractDespesaValidator):
    """REG-061 — Normaliza CPF/CNPJ antes de persistir.

    Equivalente ao normalize_cpf_cnpj do pre_save da Despesa.

    Legado: despesa.py → proponente_pre_save / validators.normalize_cpf_cnpj
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if ctx.cpf_cnpj_fornecedor:
            ctx.cpf_cnpj_fornecedor = normalize_cpf_cnpj(ctx.cpf_cnpj_fornecedor)
        return ctx
