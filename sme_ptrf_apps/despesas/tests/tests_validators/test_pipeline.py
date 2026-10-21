"""Testes para ValidatorPipeline — execução em duas fases (validate fail-fast, depois apply)
de uma sequência de validators sobre um DespesaDtoContext."""
import logging
from dataclasses import replace

import pytest

from sme_ptrf_apps.despesas.validators.base import AbstractDespesaValidator, DespesaValidationError
from sme_ptrf_apps.despesas.validators.pipeline import ValidatorPipeline
from sme_ptrf_apps.despesas.tests.tests_validators.conftest import make_ctx

pytestmark = pytest.mark.django_db


class _ValidatorRegistraChamadas(AbstractDespesaValidator):
    """Validator de teste que registra (nome, fase, ctx recebido) e opcionalmente muta o ctx."""

    def __init__(self, nome, chamadas, muta_validate=None, muta_apply=None):
        self.nome = nome
        self.chamadas = chamadas
        self.muta_validate = muta_validate
        self.muta_apply = muta_apply

    def validate(self, ctx):
        self.chamadas.append((self.nome, "validate", ctx))
        return self.muta_validate(ctx) if self.muta_validate else ctx

    def apply(self, ctx):
        self.chamadas.append((self.nome, "apply", ctx))
        return self.muta_apply(ctx) if self.muta_apply else ctx


class _ValidatorFalha(AbstractDespesaValidator):
    """Validator de teste cujo validate() sempre levanta DespesaValidationError."""

    def __init__(self, nome, chamadas, mensagem="erro de validação"):
        self.nome = nome
        self.chamadas = chamadas
        self.mensagem = mensagem

    def validate(self, ctx):
        self.chamadas.append((self.nome, "validate", ctx))
        raise DespesaValidationError(self.mensagem)


class TestExecucaoSemErros:
    def test_run_sem_validators_retorna_o_mesmo_ctx(self):
        ctx = make_ctx()

        resultado = ValidatorPipeline(validators=[]).run(ctx)

        assert resultado is ctx

    def test_run_flow_name_padrao_e_vazio(self):
        resultado = ValidatorPipeline(validators=[]).run(make_ctx())

        assert resultado is not None

    def test_run_executa_toda_a_fase_1_antes_de_iniciar_a_fase_2(self):
        chamadas = []
        v1 = _ValidatorRegistraChamadas("V1", chamadas)
        v2 = _ValidatorRegistraChamadas("V2", chamadas)

        ValidatorPipeline(validators=[v1, v2], flow_name="Fluxo").run(make_ctx())

        fases = [(nome, fase) for nome, fase, _ in chamadas]
        assert fases == [
            ("V1", "validate"),
            ("V2", "validate"),
            ("V1", "apply"),
            ("V2", "apply"),
        ]

    def test_run_encadeia_o_ctx_retornado_por_validate_entre_validators(self):
        chamadas = []

        def muta(ctx):
            return replace(ctx, numero_boletim_de_ocorrencia="alterado-por-v1")

        v1 = _ValidatorRegistraChamadas("V1", chamadas, muta_validate=muta)
        v2 = _ValidatorRegistraChamadas("V2", chamadas)
        ctx_inicial = make_ctx(numero_boletim_de_ocorrencia="original")

        ValidatorPipeline(validators=[v1, v2]).run(ctx_inicial)

        _, _, ctx_recebido_por_v2 = chamadas[1]
        assert ctx_recebido_por_v2.numero_boletim_de_ocorrencia == "alterado-por-v1"

    def test_run_encadeia_o_ctx_retornado_por_apply_entre_validators(self):
        chamadas = []

        def muta(ctx):
            return replace(ctx, numero_boletim_de_ocorrencia="alterado-no-apply-v1")

        v1 = _ValidatorRegistraChamadas("V1", chamadas, muta_apply=muta)
        v2 = _ValidatorRegistraChamadas("V2", chamadas)

        ValidatorPipeline(validators=[v1, v2]).run(make_ctx(numero_boletim_de_ocorrencia="original"))

        chamadas_apply_v2 = [c for c in chamadas if c[0] == "V2" and c[1] == "apply"]
        assert chamadas_apply_v2[0][2].numero_boletim_de_ocorrencia == "alterado-no-apply-v1"

    def test_run_retorna_o_ctx_resultante_do_ultimo_apply(self):
        def muta_apply_v2(ctx):
            return replace(ctx, numero_boletim_de_ocorrencia="final-v2")

        chamadas = []
        v1 = _ValidatorRegistraChamadas("V1", chamadas)
        v2 = _ValidatorRegistraChamadas("V2", chamadas, muta_apply=muta_apply_v2)

        resultado = ValidatorPipeline(validators=[v1, v2]).run(make_ctx())

        assert resultado.numero_boletim_de_ocorrencia == "final-v2"

    def test_run_so_aplica_apply_nos_validators_que_de_fato_executaram(self):
        chamadas = []
        v1 = _ValidatorRegistraChamadas("V1", chamadas)
        v2 = _ValidatorRegistraChamadas("V2", chamadas)

        ValidatorPipeline(validators=[v1, v2]).run(make_ctx())

        nomes_com_apply = [nome for nome, fase, _ in chamadas if fase == "apply"]
        assert nomes_com_apply == ["V1", "V2"]


class TestFalhaNaFase1:
    def test_run_interrompe_na_primeira_falha_e_propaga_a_excecao(self):
        chamadas = []
        v1 = _ValidatorRegistraChamadas("V1", chamadas)
        v2 = _ValidatorFalha("V2", chamadas, mensagem="regra violada")
        v3 = _ValidatorRegistraChamadas("V3", chamadas)

        pipeline = ValidatorPipeline(validators=[v1, v2, v3])
        ctx = make_ctx()

        with pytest.raises(DespesaValidationError, match="regra violada"):
            pipeline.run(ctx)

        nomes_chamados = [nome for nome, _, _ in chamadas]
        assert nomes_chamados == ["V1", "V2"]

    def test_run_nao_chama_apply_de_nenhum_validator_quando_ha_falha(self):
        chamadas = []
        v1 = _ValidatorRegistraChamadas("V1", chamadas)
        v2 = _ValidatorFalha("V2", chamadas)
        pipeline = ValidatorPipeline(validators=[v1, v2])
        ctx = make_ctx()

        with pytest.raises(DespesaValidationError):
            pipeline.run(ctx)

        assert not any(fase == "apply" for _, fase, _ in chamadas)

    def test_run_propaga_detail_dict_do_despesavalidationerror(self):
        v1 = _ValidatorFalha("V1", chamadas=[], mensagem={"campo": "mensagem de erro"})
        pipeline = ValidatorPipeline(validators=[v1])
        ctx = make_ctx()

        with pytest.raises(DespesaValidationError) as exc_info:
            pipeline.run(ctx)

        assert exc_info.value.detail == {"campo": "mensagem de erro"}


class TestLogging:
    def test_run_loga_inicio_execucao_de_validators_e_conclusao(self, caplog):
        chamadas = []
        v1 = _ValidatorRegistraChamadas("V1", chamadas)

        with caplog.at_level(logging.DEBUG, logger="sme_ptrf_apps.despesas.validators"):
            ValidatorPipeline(validators=[v1], flow_name="Fluxo X").run(make_ctx())

        mensagens = [r.getMessage() for r in caplog.records]
        assert any("Pipeline iniciado — 1 validators registrados" in m for m in mensagens)
        assert any("flow=Fluxo X" in m for m in mensagens)
        assert any("Fase 2: aplicando mutações de 1 validators" in m for m in mensagens)
        assert any("Pipeline concluído com sucesso" in m for m in mensagens)
        assert any("validator=_ValidatorRegistraChamadas" in m and "validate() concluído" in m for m in mensagens)
        assert any("validator=_ValidatorRegistraChamadas" in m and "apply() concluído" in m for m in mensagens)

    def test_run_loga_warning_na_falha_de_validacao_e_nao_loga_conclusao(self, caplog):
        v1 = _ValidatorFalha("V1", chamadas=[], mensagem="falhou")
        pipeline = ValidatorPipeline(validators=[v1])
        ctx = make_ctx()

        with caplog.at_level(logging.DEBUG, logger="sme_ptrf_apps.despesas.validators"):
            with pytest.raises(DespesaValidationError):
                pipeline.run(ctx)

        mensagens = [r.getMessage() for r in caplog.records]
        assert any("Falha na validação: falhou" in m for m in mensagens)
        assert not any("Pipeline concluído com sucesso" in m for m in mensagens)
