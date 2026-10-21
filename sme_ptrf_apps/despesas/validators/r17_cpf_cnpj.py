from django.core.exceptions import ValidationError as DjangoValidationError
from django.forms import ValidationError as FormsValidationError

from sme_ptrf_apps.despesas.models.validators import cpf_cnpj_validation

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class CpfCnpjValidator(AbstractDespesaValidator):
    """REG-017 — CPF/CNPJ, quando informado, deve passar na validação de formato.

    Usa o mesmo cpf_cnpj_validation do model. Valor vazio é aceito (sem comprovação
    fiscal limpa o campo — REG-027).

    Legado: despesas/models/validators.py → cpf_cnpj_validation
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        valor = (ctx.cpf_cnpj_fornecedor or "").strip()
        if not valor:
            return ctx

        try:
            cpf_cnpj_validation(valor)
        except (DjangoValidationError, FormsValidationError) as exc:
            messages = getattr(exc, "messages", None) or [str(exc)]
            raise DespesaValidationError({
                "cpf_cnpj_fornecedor": messages[0],
                "validator": self.__class__.__name__,
            }) from exc

        return ctx
