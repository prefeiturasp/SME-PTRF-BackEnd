from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class NumeroDocumentoDigitosValidator(AbstractDespesaValidator):
    """REG-016 — Número do documento só com dígitos quando o tipo exige.

    Se o tipo não solicita digitação (numero_documento_digitado=False), zera o
    número na fase apply.

    Legado (front): CadastroForm.js → validateFormDespesas
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        tipo = ctx.tipo_documento
        if not tipo:
            return ctx

        apenas_digitos = getattr(tipo, "apenas_digitos", False)
        if isinstance(tipo, dict):
            apenas_digitos = tipo.get("apenas_digitos", False)

        numero = ctx.numero_documento or ""

        if apenas_digitos and numero and not str(numero).isdigit():
            raise DespesaValidationError({
                "numero_documento": (
                    "Este campo deve conter apenas algarismos numéricos."
                ),
                "validator": self.__class__.__name__,
            })

        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        tipo = ctx.tipo_documento
        if tipo is None:
            return ctx

        digitado = getattr(tipo, "numero_documento_digitado", True)
        if isinstance(tipo, dict):
            digitado = tipo.get("numero_documento_digitado", True)

        if not digitado:
            ctx.numero_documento = ""

        return ctx
