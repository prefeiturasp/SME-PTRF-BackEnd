"""Prova de conceito: compara o veredito e o estado final entre o caminho legado
(DespesaService._atualizar_rateios, pipeline_ativa=False) e o caminho novo
(MudancaAplicacaoValidator.validate()/apply()) para o mesmo cenário de entrada.
"""
import copy

import pytest
from model_bakery import baker

from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.services.despesa_service import DespesaService
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r13_mudanca_aplicacao import MudancaAplicacaoValidator

from .conftest import make_ctx

CAPITAL = "CAPITAL"
CUSTEIO = "CUSTEIO"


def _cria_despesa_e_rateio(associacao, conta_associacao, acao_associacao, aplicacao_recurso, **extra_rateio):
    despesa = baker.make("Despesa", associacao=associacao, eh_despesa_sem_comprovacao_fiscal=False)
    rateio = baker.make(
        "RateioDespesa",
        aplicacao_recurso=aplicacao_recurso,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa,
        **extra_rateio,
    )
    return despesa, rateio


def _roda_legado(despesa, payload):
    try:
        DespesaService._atualizar_rateios(despesa, [copy.deepcopy(payload)], pipeline_ativa=False)
    except Exception as exc:
        return exc, None
    return None, RateioDespesa.objects.get(uuid=payload["uuid"])


def _roda_pipeline(despesa, payload):
    rateio = copy.deepcopy(payload)
    ctx = make_ctx(
        despesa_instance=despesa,
        rateios=[rateio],
        eh_despesa_sem_comprovacao_fiscal=despesa.eh_despesa_sem_comprovacao_fiscal,
    )
    validator = MudancaAplicacaoValidator()
    try:
        validator.validate(ctx)
    except DespesaValidationError as exc:
        return exc, None
    validator.apply(ctx)
    return None, rateio


@pytest.mark.django_db
def test_paridade_custeio_para_capital_sem_especificacao(associacao, conta_associacao, acao_associacao):
    """Mudar de CUSTEIO para CAPITAL sem informar especificação de material/serviço deve ser invalidado
    tanto no legado quanto na pipeline.
    """
    despesa_legado, rateio_legado = _cria_despesa_e_rateio(
        associacao, conta_associacao, acao_associacao, CUSTEIO, especificacao_material_servico=None
    )
    despesa_pipeline, rateio_pipeline = _cria_despesa_e_rateio(
        associacao, conta_associacao, acao_associacao, CUSTEIO, especificacao_material_servico=None
    )
    payload_base = {"aplicacao_recurso": CAPITAL, "especificacao_material_servico": None}

    erro_legado, _ = _roda_legado(despesa_legado, {**payload_base, "uuid": str(rateio_legado.uuid)})
    erro_pipeline, _ = _roda_pipeline(despesa_pipeline, {**payload_base, "uuid": str(rateio_pipeline.uuid)})

    assert erro_legado is not None
    assert erro_pipeline is not None


@pytest.mark.django_db
def test_paridade_capital_para_custeio_valido(associacao, conta_associacao, acao_associacao):
    """Mudar de CAPITAL para CUSTEIO com todos os dados obrigatórios deve passar em ambos os caminhos
    e resetar os campos exclusivos de CAPITAL para os valores default.
    """
    tipo_custeio = baker.make("TipoCusteio")
    especificacao_custeio = baker.make("EspecificacaoMaterialServico", aplicacao_recurso=CUSTEIO)

    despesa_legado, rateio_legado = _cria_despesa_e_rateio(associacao, conta_associacao, acao_associacao, CAPITAL)
    despesa_pipeline, rateio_pipeline = _cria_despesa_e_rateio(associacao, conta_associacao, acao_associacao, CAPITAL)
    payload_base = {
        "aplicacao_recurso": CUSTEIO,
        "valor_rateio": 100,
        "tipo_custeio": tipo_custeio,
        "especificacao_material_servico": especificacao_custeio,
        "numero_processo_incorporacao_capital": "ABC123",
        "quantidade_itens_capital": 5,
        "valor_item_capital": 50,
        "nao_exibir_em_rel_bens": True,
    }

    erro_legado, rateio_final_legado = _roda_legado(despesa_legado, {**payload_base, "uuid": str(rateio_legado.uuid)})
    erro_pipeline, rateio_final_pipeline = _roda_pipeline(
        despesa_pipeline, {**payload_base, "uuid": str(rateio_pipeline.uuid)}
    )

    assert erro_legado is None
    assert erro_pipeline is None
    assert rateio_final_legado.numero_processo_incorporacao_capital == rateio_final_pipeline["numero_processo_incorporacao_capital"] == ""  # noqa: E501
    assert rateio_final_legado.quantidade_itens_capital == rateio_final_pipeline["quantidade_itens_capital"] == 0
    assert rateio_final_legado.valor_item_capital == rateio_final_pipeline["valor_item_capital"] == 0
    assert rateio_final_legado.nao_exibir_em_rel_bens == rateio_final_pipeline["nao_exibir_em_rel_bens"] is False


@pytest.mark.django_db
def test_paridade_capital_para_custeio_sem_tipo_custeio(associacao, conta_associacao, acao_associacao):
    """Mudar de CAPITAL para CUSTEIO sem informar tipo_custeio deve ser invalidado em ambos os caminhos."""
    despesa_legado, rateio_legado = _cria_despesa_e_rateio(associacao, conta_associacao, acao_associacao, CAPITAL)
    despesa_pipeline, rateio_pipeline = _cria_despesa_e_rateio(
        associacao, conta_associacao, acao_associacao, CAPITAL
    )
    payload_base = {"aplicacao_recurso": CUSTEIO, "tipo_custeio": None, "especificacao_material_servico": None}

    erro_legado, _ = _roda_legado(despesa_legado, {**payload_base, "uuid": str(rateio_legado.uuid)})
    erro_pipeline, _ = _roda_pipeline(despesa_pipeline, {**payload_base, "uuid": str(rateio_pipeline.uuid)})

    assert erro_legado is not None
    assert erro_pipeline is not None


@pytest.mark.django_db
def test_paridade_custeio_para_capital_valido(associacao, conta_associacao, acao_associacao):
    """Mudar de CUSTEIO para CAPITAL com especificação válida deve passar em ambos os caminhos e
    resetar o campo tipo_custeio (exclusivo de CUSTEIO) para None/vazio.
    """
    especificacao_capital = baker.make("EspecificacaoMaterialServico", aplicacao_recurso=CAPITAL)

    despesa_legado, rateio_legado = _cria_despesa_e_rateio(associacao, conta_associacao, acao_associacao, CUSTEIO)
    despesa_pipeline, rateio_pipeline = _cria_despesa_e_rateio(
        associacao, conta_associacao, acao_associacao, CUSTEIO
    )
    payload_base = {
        "aplicacao_recurso": CAPITAL,
        "valor_rateio": 100,
        "especificacao_material_servico": especificacao_capital,
        "quantidade_itens_capital": 2,
        "valor_item_capital": 50,
    }

    erro_legado, rateio_final_legado = _roda_legado(despesa_legado, {**payload_base, "uuid": str(rateio_legado.uuid)})
    erro_pipeline, rateio_final_pipeline = _roda_pipeline(
        despesa_pipeline, {**payload_base, "uuid": str(rateio_pipeline.uuid)}
    )

    assert erro_legado is None
    assert erro_pipeline is None
    assert rateio_final_legado.tipo_custeio_id == rateio_final_pipeline.get("tipo_custeio") is None
