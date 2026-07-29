from .pipeline import ValidatorPipeline
from .r01_periodo_fechado import PeriodoFechadoValidator

# Fluxo 1 — Deleção de Bem Produzido
# Contexto: is_create=True, uuid_solicitacao_acerto=None
DELETE_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 1 — Deleção",
    validators=[
        PeriodoFechadoValidator(),
    ],
)
