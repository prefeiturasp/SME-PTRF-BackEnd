from decimal import Decimal

from sme_ptrf_apps.despesas.validators.context import DespesaDtoContext


def make_ctx(**kwargs) -> DespesaDtoContext:
    """Fábrica de DespesaDtoContext com valores padrão mínimos para testes de validators."""
    defaults = dict(
        is_create=True,
        valor_total=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        data_transacao=None,
        data_documento=None,
        retem_imposto=False,
        eh_despesa_reconhecida_pela_associacao=True,
        numero_boletim_de_ocorrencia="",
        eh_despesa_sem_comprovacao_fiscal=False,
        tipo_documento=None,
        tipo_transacao=None,
        numero_documento="",
        documento_transacao="",
        cpf_cnpj_fornecedor="",
        nome_fornecedor="",
        rateios=[],
        rateios_raw=[],
        despesas_impostos=[],
        motivos_pagamento_antecipado=[],
        outros_motivos="",
        associacao=None,
        recurso=None,
        despesa_instance=None,
    )
    defaults.update(kwargs)
    return DespesaDtoContext(**defaults)
