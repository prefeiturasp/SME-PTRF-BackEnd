from .pipeline import ValidatorPipeline
from .r00_testes import TesteBlockValidator
from .r01_recurso_obrigatorio import RecursoObrigatorioValidator
from .r02_rateios_obrigatorios import RateiosObrigatoriosValidator
from .r03_soma_valor_rateio import SomaValorRateioValidator
from .r04_soma_valor_original import SomaValorOriginalValidator
from .r05_quantidade_capital import QuantidadeCapitalValidator
from .r06_valor_original_capital import ValorOriginalCapitalValidator
from .r07_periodo_pc_devolvida import PeriodoPcDevolvidaValidator
from .r08_contas_impostos import ContasImpostosValidator
from .r08_contas_rateios import ContasRateiosValidator
from .r09_conta_acao_recurso import ContaAcaoRecursoValidator
from .r10_datas_encerramento import DatasEncerramentoValidator
from .r11_pagamento_antecipado import PagamentoAntecipadoValidator
from .r12_impostos import ImpostosValidator
from .r15_datas_futuras import DatasFuturasValidator
from .r16_numero_documento_digitos import NumeroDocumentoDigitosValidator
from .r17_cpf_cnpj import CpfCnpjValidator
from .r18_boletim_ocorrencia import BoletimOcorrenciaValidator
from .r28_data_documento_vazia import DataDocumentoVaziaValidator
from .r35_datas_imposto import DatasImpostoValidator
from .r61_normaliza_cpf_cnpj import NormalizaCpfCnpjValidator
from .r64_imposto_recurso import ImpostoRecursoValidator
from .r68_rateio_associacao import RateioAssociacaoValidator

# REG-005 deve sempre preceder REG-006 — a quantidade válida é pré-condição do cálculo.
_CAPITAL_VALIDATORS = [
    QuantidadeCapitalValidator(),       # REG-005
    ValorOriginalCapitalValidator(),    # REG-006
]

# Regras comuns aos quatro fluxos.
_CORE_VALIDATORS = [
    RateiosObrigatoriosValidator(),     # REG-002
    SomaValorRateioValidator(),         # REG-003
    SomaValorOriginalValidator(),       # REG-004
    *_CAPITAL_VALIDATORS,               # REG-005, REG-006
    DatasFuturasValidator(),            # REG-015
    NumeroDocumentoDigitosValidator(),  # REG-016
    CpfCnpjValidator(),                 # REG-017
    BoletimOcorrenciaValidator(),       # REG-018
    DatasImpostoValidator(),            # REG-035
    DataDocumentoVaziaValidator(),      # REG-028 (apply)
    NormalizaCpfCnpjValidator(),        # REG-061 (apply)
    ImpostoRecursoValidator(),          # REG-064 (apply)
    RateioAssociacaoValidator(),        # REG-068 (apply)
]


# Fluxo 1 — Criação de despesa (sem vínculo de Solicitação de Acerto)
CREATE_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 1 — Criação",
    validators=[
        RecursoObrigatorioValidator(),      # REG-001 — apenas create
        *_CORE_VALIDATORS,
        DatasEncerramentoValidator(),       # REG-010
        PagamentoAntecipadoValidator(),     # REG-011
        PeriodoPcDevolvidaValidator(),      # REG-007
        ContasRateiosValidator(),           # REG-008
        ContasImpostosValidator(),          # REG-008
        ContaAcaoRecursoValidator(),        # REG-009
        ImpostosValidator(),                # REG-012
        TesteBlockValidator(),              # R00
    ],
)


# Fluxo 2 — Edição de despesa (sem vínculo de Solicitação de Acerto)
# Contexto: is_create=False, uuid_solicitacao_acerto=None
# Omite RecursoObrigatorio; MudancaAplicacao (REG-013) ainda comentada.
UPDATE_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 2 — Edição",
    validators=[
        *_CORE_VALIDATORS,
        # DatasEncerramentoValidator(),       # REG-010
        # PagamentoAntecipadoValidator(),     # REG-011
        # PeriodoPcDevolvidaValidator(),      # REG-007
        # ContasRateiosValidator(),           # REG-008
        # ContasImpostosValidator(),          # REG-008
        # ContaAcaoRecursoValidator(),        # REG-009
        # MudancaAplicacaoValidator(),        # REG-013
        # ImpostosValidator(),                # REG-012
        TesteBlockValidator(),              # R00
    ],
)

# Fluxo 3 — Criação de despesa com vínculo de Solicitação de Acerto
CREATE_ACERTO_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 3 — Criação via Acerto",
    validators=[
        RecursoObrigatorioValidator(),      # REG-001
        *_CORE_VALIDATORS,
        # DatasEncerramentoValidator(),       # REG-010
        # PagamentoAntecipadoValidator(),     # REG-011
        # PeriodoPcDevolvidaValidator(),      # REG-007
        # ContasRateiosValidator(),           # REG-008
        # ContasImpostosValidator(),          # REG-008
        # ContaAcaoRecursoValidator(),        # REG-009
        # ImpostosValidator(),                # REG-012
        TesteBlockValidator(),              # R00
    ],
)

# Fluxo 4 — Edição de despesa com vínculo de Solicitação de Acerto
UPDATE_ACERTO_PIPELINE = ValidatorPipeline(
    flow_name="Fluxo 4 — Edição via Acerto",
    validators=[
        *_CORE_VALIDATORS,
        # DatasEncerramentoValidator(),       # REG-010
        # PagamentoAntecipadoValidator(),     # REG-011
        # PeriodoPcDevolvidaValidator(),      # REG-007
        # ContasRateiosValidator(),           # REG-008
        # ContasImpostosValidator(),          # REG-008
        # ContaAcaoRecursoValidator(),        # REG-009
        # MudancaAplicacaoValidator(),        # REG-013
        # ImpostosValidator(),                # REG-012
        TesteBlockValidator(),              # R00
    ],
)
