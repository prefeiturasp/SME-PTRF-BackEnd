from sme_ptrf_apps.despesas.validators.r61_normaliza_cpf_cnpj import (
    NormalizaCpfCnpjValidator,
)

from .conftest import make_ctx


def test_apply_cnpj_mascarado_fica_maiusculo():
    """normalize_cpf_cnpj upper-caseia CNPJ já mascarado (comportamento do legado)."""
    validator = NormalizaCpfCnpjValidator()
    ctx = make_ctx(cpf_cnpj_fornecedor="12.abc.678/0001-95")
    result = validator.apply(ctx)
    assert result.cpf_cnpj_fornecedor == "12.ABC.678/0001-95"


def test_apply_vazio_nao_altera():
    validator = NormalizaCpfCnpjValidator()
    ctx = make_ctx(cpf_cnpj_fornecedor="")
    result = validator.apply(ctx)
    assert result.cpf_cnpj_fornecedor == ""


def test_apply_cpf_sem_mascara_permanece():
    """CPF sem máscara não é reformatado por normalize_cpf_cnpj (legado)."""
    validator = NormalizaCpfCnpjValidator()
    ctx = make_ctx(cpf_cnpj_fornecedor="12345678909")
    result = validator.apply(ctx)
    assert result.cpf_cnpj_fornecedor == "12345678909"
