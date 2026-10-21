from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext
from .logger import ContextualLogger


class ValidatorPipeline:
    """Executa uma sequência de validators sobre um DespesaDtoContext em duas fases.

    Fase 1 — validação (fail-fast):
        Todos os validators executam `validate()` em ordem.
        Na primeira falha (DespesaValidationError), a fase 2 não ocorre.

    Fase 2 — mutações:
        Executada somente se a fase 1 completou sem erros.
        Chama `apply()` nos validators que efetivamente rodaram (mesma ordem).
        Mutações ficam co-localizadas com a regra que as origina, mas isoladas da validação.

    A separação create/update é feita pela composição dos pipelines em pipelines.py.
    """

    def __init__(self, validators: list[AbstractDespesaValidator], flow_name: str = ""):
        self._validators = validators
        self._flow_name = flow_name

    def run(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        log = ContextualLogger.from_context(ctx, flow_name=self._flow_name)
        log.info(f"Pipeline iniciado — {len(self._validators)} validators registrados")

        executed = []

        # Fase 1: validações (fail-fast — interrompe ao primeiro erro)
        for validator in self._validators:
            validator_name = type(validator).__name__
            v_log = log.with_validator(validator_name)

            v_log.debug("Fase 1: validate()")
            try:
                ctx = validator.validate(ctx)
                executed.append(validator)
                v_log.debug("validate() concluído")
            except DespesaValidationError as exc:
                v_log.warning(f"Falha na validação: {exc.detail}")
                raise

        # Fase 2: mutações (somente se toda a fase 1 passou sem erros)
        log.debug(f"Fase 2: aplicando mutações de {len(executed)} validators")
        for validator in executed:
            v_log = log.with_validator(type(validator).__name__)
            ctx = validator.apply(ctx)
            v_log.debug("apply() concluído")

        log.info("Pipeline concluído com sucesso")
        return ctx
