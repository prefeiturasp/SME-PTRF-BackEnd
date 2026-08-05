from sme_ptrf_apps.despesas.validators.r64_imposto_recurso import ImpostoRecursoValidator

from .conftest import make_ctx


def test_apply_copia_recurso_em_imposto_novo():
    validator = ImpostoRecursoValidator()
    recurso = object()
    imposto = {"valor_total": 10}
    ctx = make_ctx(retem_imposto=True, recurso=recurso, despesas_impostos=[imposto])
    validator.apply(ctx)
    assert imposto["recurso"] is recurso


def test_apply_nao_recopia_imposto_existente():
    validator = ImpostoRecursoValidator()
    recurso = object()
    imposto = {"uuid": "abc", "recurso": "antigo"}
    ctx = make_ctx(retem_imposto=True, recurso=recurso, despesas_impostos=[imposto])
    validator.apply(ctx)
    assert imposto["recurso"] == "antigo"


def test_apply_ignora_sem_retencao():
    validator = ImpostoRecursoValidator()
    imposto = {}
    ctx = make_ctx(retem_imposto=False, recurso=object(), despesas_impostos=[imposto])
    validator.apply(ctx)
    assert "recurso" not in imposto
