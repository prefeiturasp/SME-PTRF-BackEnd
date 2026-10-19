from .pipeline import ValidatorPipeline
from .r00_possui_associacao import BemProduzidoPossuiAssociacaoValidator
from .r01_periodo_fechado import VerificarSeTodosPeriodosEstaoFechadosValidator
from .r03_bloqueio_edicao_completo import BloqueioEdicaoBemProduzidoCompletoPeriodoFechadoValidator

# Fluxo 1 — Deleção de Bem Produzido
DELETE_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 1 — Deleção",
    validators=[
        BemProduzidoPossuiAssociacaoValidator(),
        VerificarSeTodosPeriodosEstaoFechadosValidator(),
    ],
)

# Fluxo 2 — Edição de Bem Produzido
EDIT_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 2 — Edição",
    validators=[
        BemProduzidoPossuiAssociacaoValidator(),
        BloqueioEdicaoBemProduzidoCompletoPeriodoFechadoValidator(),
    ],
)
