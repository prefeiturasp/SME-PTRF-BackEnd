"""Testes para ContextualLogger — LoggerAdapter que prefixa mensagens do pipeline de
validação de despesas com o contexto (fluxo, is_create, is_acerto, despesa, associação, recurso)."""
import logging
from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.logger import ContextualLogger, _DEFAULT_LOGGER
from sme_ptrf_apps.despesas.tests.tests_validators.conftest import make_ctx

pytestmark = pytest.mark.django_db


class TestProcess:
    def test_process_prefixa_mensagem_com_o_contexto_na_ordem_de_insercao(self):
        log = ContextualLogger(logging.getLogger("teste"), {"flow": "Fluxo 1", "is_create": True})

        mensagem, kwargs = log.process("Pipeline iniciado", {})

        assert mensagem == "[flow=Fluxo 1 | is_create=True] Pipeline iniciado"
        assert kwargs == {}

    def test_process_com_contexto_vazio_nao_deixa_espaco_sobrando(self):
        log = ContextualLogger(logging.getLogger("teste"), {})

        mensagem, kwargs = log.process("mensagem sem contexto", {})

        assert mensagem == "[] mensagem sem contexto"

    def test_process_preserva_kwargs_recebidos(self):
        log = ContextualLogger(logging.getLogger("teste"), {"flow": "Fluxo 1"})

        _, kwargs = log.process("msg", {"exc_info": True})

        assert kwargs == {"exc_info": True}


class TestFromContextCamposMinimos:
    def test_from_context_sem_dados_opcionais_traz_apenas_flow_is_create_is_acerto(self):
        ctx = make_ctx(is_create=True)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1 — Criação")

        assert log.extra["flow"] == "Fluxo 1 — Criação"
        assert log.extra["is_create"] is True
        assert log.extra["is_acerto"] is False
        assert "despesa_id" not in log.extra
        assert "despesa_uuid" not in log.extra
        assert "recurso_id" not in log.extra
        assert "solicitacao_acerto" not in log.extra
        assert "associacao_id" not in log.extra
        assert "associacao_uuid" not in log.extra

    def test_from_context_usa_o_logger_padrao_quando_base_logger_nao_informado(self):
        ctx = make_ctx()

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert log.logger is _DEFAULT_LOGGER

    def test_from_context_usa_base_logger_informado(self):
        ctx = make_ctx()
        logger_customizado = logging.getLogger("sme_ptrf_apps.despesas.validators.teste")

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1", base_logger=logger_customizado)

        assert log.logger is logger_customizado

    def test_from_context_operation_id_concatena_os_campos_ja_presentes(self):
        ctx = make_ctx(is_create=False)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 2 — Edição")

        assert log.extra["operation_id"] == "flow=Fluxo 2 — Edição | is_create=False | is_acerto=False"


class TestFromContextDespesaInstance:
    def test_from_context_com_despesa_instance_adiciona_id_e_uuid(self):
        despesa = SimpleNamespace(id=1, uuid="uuid-despesa", recurso=None)
        ctx = make_ctx(is_create=False, despesa_instance=despesa)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 2")

        assert log.extra["despesa_id"] == 1
        assert log.extra["despesa_uuid"] == "uuid-despesa"


class TestFromContextRecurso:
    def test_from_context_usa_recurso_direto_do_contexto(self):
        recurso = SimpleNamespace(id=42)
        ctx = make_ctx(recurso=recurso)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert log.extra["recurso_id"] == 42

    def test_from_context_sem_atributo_id_usa_str_do_recurso(self):
        ctx = make_ctx(recurso="recurso-sem-id")

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert log.extra["recurso_id"] == "recurso-sem-id"

    def test_from_context_sem_recurso_direto_usa_recurso_da_despesa_instance(self):
        recurso_da_despesa = SimpleNamespace(id=7)
        despesa = SimpleNamespace(id=1, uuid="uuid-despesa", recurso=recurso_da_despesa)
        ctx = make_ctx(is_create=False, recurso=None, despesa_instance=despesa)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 2")

        assert log.extra["recurso_id"] == 7

    def test_from_context_sem_recurso_e_sem_despesa_instance_nao_adiciona_recurso_id(self):
        ctx = make_ctx(recurso=None, despesa_instance=None)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert "recurso_id" not in log.extra


class TestFromContextSolicitacaoAcerto:
    def test_from_context_com_uuid_solicitacao_acerto_marca_solicitacao_acerto_e_is_acerto(self):
        ctx = make_ctx(uuid_solicitacao_acerto="uuid-solicitacao")

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 3")

        assert log.extra["solicitacao_acerto"] == "uuid-solicitacao"
        assert log.extra["is_acerto"] is True

    def test_from_context_sem_uuid_solicitacao_acerto_nao_adiciona_a_chave(self):
        ctx = make_ctx(uuid_solicitacao_acerto=None)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert "solicitacao_acerto" not in log.extra


class TestFromContextAssociacao:
    def test_from_context_com_associacao_com_id_e_uuid(self):
        associacao = SimpleNamespace(id=9, uuid="uuid-associacao")
        ctx = make_ctx(associacao=associacao)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert log.extra["associacao_id"] == 9
        assert log.extra["associacao_uuid"] == "uuid-associacao"

    def test_from_context_com_associacao_sem_id_ou_uuid_usa_str_dela_mesma(self):
        ctx = make_ctx(associacao="associacao-crua")

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert log.extra["associacao_id"] == "associacao-crua"
        assert log.extra["associacao_uuid"] == "associacao-crua"

    def test_from_context_sem_associacao_nao_adiciona_as_chaves(self):
        ctx = make_ctx(associacao=None)

        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        assert "associacao_id" not in log.extra
        assert "associacao_uuid" not in log.extra


class TestWithValidator:
    def test_with_validator_adiciona_a_chave_validator_preservando_o_restante(self):
        ctx = make_ctx(is_create=True)
        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        log_validator = log.with_validator("RateiosObrigatoriosValidator")

        assert log_validator.extra["validator"] == "RateiosObrigatoriosValidator"
        assert log_validator.extra["flow"] == "Fluxo 1"
        assert log_validator.extra["is_create"] is True

    def test_with_validator_nao_muta_o_logger_original(self):
        ctx = make_ctx()
        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        log.with_validator("ValidatorX")

        assert "validator" not in log.extra

    def test_with_validator_reaproveita_o_mesmo_logger_interno(self):
        ctx = make_ctx()
        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        log_validator = log.with_validator("ValidatorX")

        assert log_validator.logger is log.logger

    def test_with_validator_retorna_uma_nova_instancia(self):
        ctx = make_ctx()
        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1")

        log_validator = log.with_validator("ValidatorX")

        assert log_validator is not log


class TestIntegracaoComLogging:
    def test_log_info_emite_mensagem_com_contexto_formatado(self, caplog):
        ctx = make_ctx(is_create=True)
        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1 — Criação")

        with caplog.at_level(logging.INFO, logger="sme_ptrf_apps.despesas.validators"):
            log.info("Pipeline iniciado")

        assert len(caplog.records) == 1
        mensagem = caplog.records[0].getMessage()
        assert mensagem.startswith("[flow=Fluxo 1 — Criação | is_create=True | is_acerto=False")
        assert mensagem.endswith("Pipeline iniciado")

    def test_log_com_validator_inclui_o_validator_na_mensagem(self, caplog):
        ctx = make_ctx(is_create=True)
        log = ContextualLogger.from_context(ctx, flow_name="Fluxo 1").with_validator("MeuValidator")

        with caplog.at_level(logging.DEBUG, logger="sme_ptrf_apps.despesas.validators"):
            log.debug("Executando")

        mensagem = caplog.records[0].getMessage()
        assert "validator=MeuValidator" in mensagem
        assert mensagem.endswith("Executando")
