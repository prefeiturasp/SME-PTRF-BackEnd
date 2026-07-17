from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class BoletimOcorrenciaValidator(AbstractDespesaValidator):
    """REG-018 — Despesa não reconhecida exige número do boletim de ocorrência.

    Legado (front): CadastroForm.js → validacoesPersonalizadas
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — se a despesa não é reconhecida, exige boletim preenchido.

        Levanta DespesaValidationError com detail no campo numero_boletim_de_ocorrencia.
        """
        if ctx.eh_despesa_reconhecida_pela_associacao:
            return ctx

        if not (ctx.numero_boletim_de_ocorrencia or "").strip():
            raise DespesaValidationError({
                "numero_boletim_de_ocorrencia": (
                    "Digite um número de boletim de ocorrência"
                ),
                "validator": self.__class__.__name__,
            })

        return ctx
