from types import SimpleNamespace

import pytest
from model_bakery import baker

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r13_mudanca_aplicacao import MudancaAplicacaoValidator

from .conftest import make_ctx

CAPITAL = "CAPITAL"
CUSTEIO = "CUSTEIO"


@pytest.fixture
def validator():
    return MudancaAplicacaoValidator()


def _despesa_normal():
    return SimpleNamespace(eh_despesa_sem_comprovacao_fiscal=False)


def _despesa_sem_comprovacao():
    return SimpleNamespace(eh_despesa_sem_comprovacao_fiscal=True)


# ──────────────────────────── Casos sem DB ────────────────────────────


def test_valida_ok_sem_despesa_instance(validator):
    # Sem instância → validator é no-op (somente presente nos UPDATE_PIPELINEs)
    ctx = make_ctx(despesa_instance=None)
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_rateio_sem_uuid(validator):
    ctx = make_ctx(
        rateios=[{"aplicacao_recurso": CUSTEIO}],
        despesa_instance=_despesa_normal(),
    )
    result = validator.validate(ctx)
    assert result is ctx


# ──────────────────────────── Casos com DB ────────────────────────────


@pytest.mark.django_db
def test_valida_ok_mesma_aplicacao(validator, associacao, conta_associacao, acao_associacao):
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CAPITAL,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    ctx = make_ctx(
        rateios=[{"uuid": str(rateio_db.uuid), "aplicacao_recurso": CAPITAL}],
        despesa_instance=_despesa_normal(),
    )
    result = validator.validate(ctx)
    assert result is ctx


@pytest.mark.django_db
def test_valida_ok_capital_para_custeio_com_sem_exigencia(validator, associacao, conta_associacao, acao_associacao):
    # eh_despesa_sem_comprovacao_fiscal=True → sem_exigencia → pula validação
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CAPITAL,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        saida_de_recurso_externo=False,
    )
    despesa = SimpleNamespace(eh_despesa_sem_comprovacao_fiscal=True)
    ctx = make_ctx(
        rateios=[{"uuid": str(rateio_db.uuid), "aplicacao_recurso": CUSTEIO}],
        despesa_instance=despesa,
        eh_despesa_sem_comprovacao_fiscal=True
    )
    result = validator.validate(ctx)
    assert result is ctx


@pytest.mark.django_db
def test_valida_erro_capital_para_custeio_sem_tipo_custeio(validator, associacao, conta_associacao, acao_associacao):
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CAPITAL,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    ctx = make_ctx(
        rateios=[{
            "uuid": str(rateio_db.uuid),
            "aplicacao_recurso": CUSTEIO,
            "tipo_custeio": None,
            "especificacao_material_servico": None,
        }],
        despesa_instance=_despesa_normal(),
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


@pytest.mark.django_db
def test_valida_erro_capital_para_custeio_especificacao_capital(
    validator, associacao, conta_associacao, acao_associacao
):
    # tipo_custeio preenchido mas especificação é CAPITAL (não CUSTEIO)
    tipo_custeio = baker.make("TipoCusteio")
    especificacao_capital = baker.make("EspecificacaoMaterialServico", aplicacao_recurso=CAPITAL)
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CAPITAL,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    ctx = make_ctx(
        rateios=[{
            "uuid": str(rateio_db.uuid),
            "aplicacao_recurso": CUSTEIO,
            "tipo_custeio": tipo_custeio,
            "especificacao_material_servico": especificacao_capital,
        }],
        despesa_instance=_despesa_normal(),
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


@pytest.mark.django_db
def test_valida_erro_custeio_para_capital_sem_especificacao(validator, associacao, conta_associacao, acao_associacao):
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CUSTEIO,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        especificacao_material_servico=None,
    )
    ctx = make_ctx(
        rateios=[{
            "uuid": str(rateio_db.uuid),
            "aplicacao_recurso": CAPITAL,
            "especificacao_material_servico": None,
        }],
        despesa_instance=_despesa_normal(),
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


@pytest.mark.django_db
def test_valida_erro_custeio_para_capital_especificacao_custeio(
    validator, associacao, conta_associacao, acao_associacao
):
    especificacao_custeio = baker.make("EspecificacaoMaterialServico", aplicacao_recurso=CUSTEIO)
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CUSTEIO,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    ctx = make_ctx(
        rateios=[{
            "uuid": str(rateio_db.uuid),
            "aplicacao_recurso": CAPITAL,
            "especificacao_material_servico": especificacao_custeio,
        }],
        despesa_instance=_despesa_normal(),
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


@pytest.mark.django_db
def test_apply_capital_para_custeio_reseta_campos(validator, associacao, conta_associacao, acao_associacao):
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CAPITAL,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    rateio = {
        "uuid": str(rateio_db.uuid),
        "aplicacao_recurso": CUSTEIO,
        "numero_processo_incorporacao_capital": "ABC123",
        "quantidade_itens_capital": 5,
        "valor_item_capital": 50,
        "nao_exibir_em_rel_bens": True,
    }
    ctx = make_ctx(rateios=[rateio], despesa_instance=_despesa_normal())
    validator.apply(ctx)
    assert rateio["numero_processo_incorporacao_capital"] == ""
    assert rateio["quantidade_itens_capital"] == 0
    assert rateio["valor_item_capital"] == 0
    assert rateio["nao_exibir_em_rel_bens"] is False


@pytest.mark.django_db
def test_apply_custeio_para_capital_reseta_tipo_custeio(validator, associacao, conta_associacao, acao_associacao):
    tipo_custeio = baker.make("TipoCusteio")
    rateio_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CUSTEIO,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    rateio = {
        "uuid": str(rateio_db.uuid),
        "aplicacao_recurso": CAPITAL,
        "tipo_custeio": tipo_custeio,
    }
    ctx = make_ctx(rateios=[rateio], despesa_instance=_despesa_normal())
    validator.apply(ctx)
    assert rateio["tipo_custeio"] is None


@pytest.mark.django_db
def test_valida_ok_imposto_sem_uuid(validator, associacao, conta_associacao, acao_associacao):
    """Imposto novo (sem uuid, fluxo de criação) não tem estado anterior pra comparar — ignorado."""
    imposto = {
        "rateios": [{
            "aplicacao_recurso": CUSTEIO,
            "tipo_custeio": None,
            "especificacao_material_servico": None,
        }],
    }
    ctx = make_ctx(despesa_instance=None, despesas_impostos=[imposto])
    result = validator.validate(ctx)
    assert result is ctx


@pytest.mark.django_db
def test_valida_ok_imposto_uuid_nao_encontrado(validator):
    """Imposto com uuid que não existe no banco é ignorado, sem erro."""
    imposto = {"uuid": "00000000-0000-0000-0000-000000000000", "rateios": []}
    ctx = make_ctx(despesa_instance=None, despesas_impostos=[imposto])
    result = validator.validate(ctx)
    assert result is ctx


@pytest.mark.django_db
def test_valida_erro_imposto_custeio_para_capital_sem_especificacao(
    validator, associacao, conta_associacao, acao_associacao
):
    """Rateio de despesa de imposto também é validado — ctx.rateios (despesa principal) fica vazio."""
    despesa_imposto_db = baker.make(
        "Despesa",
        associacao=associacao,
        eh_despesa_sem_comprovacao_fiscal=False,
    )
    rateio_imposto_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CUSTEIO,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        especificacao_material_servico=None,
    )
    imposto = {
        "uuid": str(despesa_imposto_db.uuid),
        "rateios": [{
            "uuid": str(rateio_imposto_db.uuid),
            "aplicacao_recurso": CAPITAL,
            "especificacao_material_servico": None,
        }],
    }
    ctx = make_ctx(despesa_instance=None, rateios=[], despesas_impostos=[imposto])
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


@pytest.mark.django_db
def test_valida_ok_imposto_mudanca_valida(validator, associacao, conta_associacao, acao_associacao):
    """Mudança de aplicação no rateio do imposto com especificação/tipo_custeio corretos não levanta erro."""
    despesa_imposto_db = baker.make(
        "Despesa",
        associacao=associacao,
        eh_despesa_sem_comprovacao_fiscal=False,
    )
    tipo_custeio = baker.make("TipoCusteio")
    especificacao_custeio = baker.make("EspecificacaoMaterialServico", aplicacao_recurso=CUSTEIO)
    rateio_imposto_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CAPITAL,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    imposto = {
        "uuid": str(despesa_imposto_db.uuid),
        "rateios": [{
            "uuid": str(rateio_imposto_db.uuid),
            "aplicacao_recurso": CUSTEIO,
            "tipo_custeio": tipo_custeio,
            "especificacao_material_servico": especificacao_custeio,
        }],
    }
    ctx = make_ctx(despesa_instance=None, despesas_impostos=[imposto])
    result = validator.validate(ctx)
    assert result is ctx


@pytest.mark.django_db
def test_apply_imposto_reseta_campos(validator, associacao, conta_associacao, acao_associacao):
    """apply() reseta campos incompatíveis dentro de despesas_impostos[i]['rateios'], não só em ctx.rateios."""
    despesa_imposto_db = baker.make(
        "Despesa",
        associacao=associacao,
        eh_despesa_sem_comprovacao_fiscal=False,
    )
    rateio_imposto_db = baker.make(
        "RateioDespesa",
        aplicacao_recurso=CAPITAL,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )
    rateio_imposto = {
        "uuid": str(rateio_imposto_db.uuid),
        "aplicacao_recurso": CUSTEIO,
        "numero_processo_incorporacao_capital": "XYZ789",
        "quantidade_itens_capital": 3,
        "valor_item_capital": 10,
        "nao_exibir_em_rel_bens": True,
    }
    imposto = {"uuid": str(despesa_imposto_db.uuid), "rateios": [rateio_imposto]}
    ctx = make_ctx(despesa_instance=None, despesas_impostos=[imposto])
    validator.apply(ctx)
    assert rateio_imposto["numero_processo_incorporacao_capital"] == ""
    assert rateio_imposto["quantidade_itens_capital"] == 0
    assert rateio_imposto["valor_item_capital"] == 0
    assert rateio_imposto["nao_exibir_em_rel_bens"] is False
