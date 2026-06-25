from .pipeline import ValidatorPipeline
from .r01_rateios_obrigatorios import RateiosObrigatoriosValidator
from .r02_recurso_obrigatorio import RecursoObrigatorioValidator
from .r04_soma_rateios import SomaRateiosValidator
from .r05_quantidade_capital import QuantidadeCapitalValidator
from .r06a_valor_rateio_capital import ValorRateioCapitalValidator
from .r06b_valor_original_capital import ValorOriginalCapitalValidator
from .r16_impostos import ImpostosValidator
from .r42_saldos import SaldosValidator
from .r13_datas_encerramento import DatasEncerramentoValidator
from .r14_pagamento_antecipado import PagamentoAntecipadoValidator
from .r07_periodo_pc_devolvida import PeriodoPcDevolvidaValidator
from .r08_contas_rateios import ContasRateiosValidator
from .r10_contas_impostos import ContasImpostosValidator
from .r12_conta_acao_recurso import ContaAcaoRecursoValidator
from .r17_mudanca_aplicacao import MudancaAplicacaoValidator

# R05 deve sempre preceder R06a e R06b — a quantidade válida é pré-condição dos cálculos.
_CAPITAL_VALIDATORS = [
    QuantidadeCapitalValidator(),       # R05
    ValorRateioCapitalValidator(),      # R06a
    ValorOriginalCapitalValidator(),    # R06b
]


# Fluxo 1 — Criação de despesa (sem vínculo de Solicitação de Acerto)
# Contexto: is_create=True, uuid_solicitacao_acerto=None
CREATE_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 1 — Criação",
    validators=[
        # RecursoObrigatorioValidator(),      # R02  — apenas create
        # RateiosObrigatoriosValidator(),     # R01
        # SomaRateiosValidator(),             # R04a, R04b
        # *_CAPITAL_VALIDATORS,               # R05, R06a, R06b
        # DatasEncerramentoValidator(),       # R13
        # PagamentoAntecipadoValidator(),     # R14, R15
        # PeriodoPcDevolvidaValidator(),      # R07  — injeta ctx.periodo
        # ContasRateiosValidator(),           # R08, R09
        # ContasImpostosValidator(),          # R10, R11
        # ContaAcaoRecursoValidator(),        # R12
        # ImpostosValidator(),                # R16
        # SaldosValidator(),                  # R42-R45
    ],
)


# Fluxo 2 — Edição de despesa (sem vínculo de Solicitação de Acerto)
# Contexto: is_create=False, uuid_solicitacao_acerto=None
# Inclui MudancaAplicacaoValidator (apenas update) e omite RecursoObrigatorio
UPDATE_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 2 — Edição",
    validators=[
        # RateiosObrigatoriosValidator(),     # R01
        # SomaRateiosValidator(),             # R04a, R04b
        # *_CAPITAL_VALIDATORS,               # R05, R06a, R06b
        # DatasEncerramentoValidator(),       # R13
        # PagamentoAntecipadoValidator(),     # R14, R15
        # PeriodoPcDevolvidaValidator(),      # R07  — injeta ctx.periodo
        # ContasRateiosValidator(),           # R08, R09
        # ContasImpostosValidator(),          # R10, R11
        # ContaAcaoRecursoValidator(),        # R12
        # MudancaAplicacaoValidator(),        # R17-R21  — apenas update
        # ImpostosValidator(),                # R16
        # SaldosValidator(),                  # R42-R45
    ],
)

# Fluxo 3 — Criação de despesa com vínculo de Solicitação de Acerto
# Contexto: is_create=True, uuid_solicitacao_acerto=<uuid>
# Originado de uma análise DRE que solicitou inclusão de novo gasto.
# Estrutura idêntica ao Fluxo 1 — instância separada para permitir independência de
# regras de negócios sem impactar o fluxo normal de criação.
CREATE_ACERTO_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 3 — Criação via Acerto",
    validators=[
        # RecursoObrigatorioValidator(),      # R02  — apenas create
        # RateiosObrigatoriosValidator(),     # R01
        # SomaRateiosValidator(),             # R04a, R04b
        # *_CAPITAL_VALIDATORS,               # R05, R06a, R06b
        # DatasEncerramentoValidator(),       # R13
        # PagamentoAntecipadoValidator(),     # R14, R15
        # PeriodoPcDevolvidaValidator(),      # R07  — injeta ctx.periodo
        # ContasRateiosValidator(),           # R08, R09
        # ContasImpostosValidator(),          # R10, R11
        # ContaAcaoRecursoValidator(),        # R12
        # ImpostosValidator(),                # R16
        # SaldosValidator(),                  # R42-R45
    ],
)

# Fluxo 4 — Edição de despesa com vínculo de Solicitação de Acerto
# Contexto: is_create=False, uuid_solicitacao_acerto=<uuid>
# Originado de uma análise DRE que solicitou ajuste em gasto existente.
# Estrutura idêntica ao Fluxo 2 — instância separada para permitir independência de
# regras de negócios sem impactar o fluxo normal de edição.
UPDATE_ACERTO_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 4 — Edição via Acerto",
    validators=[
        # RateiosObrigatoriosValidator(),     # R01
        # SomaRateiosValidator(),             # R04a, R04b
        # *_CAPITAL_VALIDATORS,               # R05, R06a, R06b
        # DatasEncerramentoValidator(),       # R13
        # PagamentoAntecipadoValidator(),     # R14, R15
        # PeriodoPcDevolvidaValidator(),      # R07  — injeta ctx.periodo
        # ContasRateiosValidator(),           # R08, R09
        # ContasImpostosValidator(),          # R10, R11
        # ContaAcaoRecursoValidator(),        # R12
        # MudancaAplicacaoValidator(),        # R17-R21  — apenas update
        # ImpostosValidator(),                # R16
        # SaldosValidator(),                  # R42-R45
    ],
)
