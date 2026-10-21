"""Testes para DespesaContextBuilder — montagem do DespesaDtoContext a partir do
validated_data do serializer, com fallback para a instância em updates."""
from decimal import Decimal
from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.builder import DespesaContextBuilder

pytestmark = pytest.mark.django_db


def _instancia_despesa(**overrides) -> SimpleNamespace:
    """Duble de uma instância de Despesa com todos os campos que o builder consulta via getattr."""
    valores = dict(
        valor_total=Decimal("200.00"),
        valor_recursos_proprios=Decimal("20.00"),
        data_transacao="2024-03-10",
        data_documento="2024-03-09",
        retem_imposto=True,
        eh_despesa_reconhecida_pela_associacao=True,
        numero_boletim_de_ocorrencia="BO-1",
        eh_despesa_sem_comprovacao_fiscal=True,
        tipo_documento="tipo-doc-instancia",
        tipo_transacao="tipo-transacao-instancia",
        numero_documento="999",
        documento_transacao="doc-transacao-instancia",
        cpf_cnpj_fornecedor="11.478.276/0001-04",
        nome_fornecedor="Fornecedor da instância",
        rateios=["rateio-instancia"],
        despesas_impostos=["imposto-instancia"],
        motivos_pagamento_antecipado=["motivo-instancia"],
        outros_motivos_pagamento_antecipado="outro motivo da instância",
        associacao="associacao-instancia",
        valor_original=Decimal("150.00"),
    )
    valores.update(overrides)
    return SimpleNamespace(**valores)


class TestBuildCreate:
    def test_build_create_sem_dados_aplica_defaults(self):
        ctx = DespesaContextBuilder.build(validated_data={})

        assert ctx.is_create is True
        assert ctx.despesa_instance is None
        assert ctx.valor_total == Decimal("0")
        assert ctx.valor_recursos_proprios == Decimal("0")
        assert ctx.valor_original is None
        assert ctx.retem_imposto is False
        assert ctx.eh_despesa_reconhecida_pela_associacao is True
        assert ctx.numero_boletim_de_ocorrencia == ""
        assert ctx.eh_despesa_sem_comprovacao_fiscal is False
        assert ctx.tipo_documento is None
        assert ctx.tipo_transacao is None
        assert ctx.numero_documento == ""
        assert ctx.documento_transacao == ""
        assert ctx.cpf_cnpj_fornecedor == ""
        assert ctx.nome_fornecedor == ""
        assert ctx.rateios == []
        assert ctx.rateios_raw == []
        assert ctx.despesas_impostos == []
        assert ctx.motivos_pagamento_antecipado == []
        assert ctx.outros_motivos is None
        assert ctx.associacao is None
        assert ctx.recurso is None
        assert ctx.uuid_solicitacao_acerto is None
        assert ctx.is_acerto is False

    def test_build_create_com_dados_completos_preenche_context(self):
        recurso = object()
        validated_data = {
            "valor_total": 150.5,
            "valor_recursos_proprios": 10,
            "valor_original": "150.50",
            "data_transacao": "2024-03-10",
            "data_documento": "2024-03-09",
            "retem_imposto": True,
            "eh_despesa_reconhecida_pela_associacao": False,
            "numero_boletim_de_ocorrencia": "BO-1",
            "eh_despesa_sem_comprovacao_fiscal": True,
            "tipo_documento": "tipo-doc",
            "tipo_transacao": "tipo-transacao",
            "numero_documento": "123456",
            "documento_transacao": "doc-transacao",
            "cpf_cnpj_fornecedor": "11.478.276/0001-04",
            "nome_fornecedor": "Fornecedor SA",
            "rateios": ["rateio-1"],
            "despesas_impostos": ["imposto-1"],
            "motivos_pagamento_antecipado": ["motivo-1"],
            "outros_motivos_pagamento_antecipado": "outro motivo",
            "associacao": "associacao-1",
        }

        ctx = DespesaContextBuilder.build(
            validated_data=validated_data,
            recurso=recurso,
            initial_data={"rateios": ["uuid-1", "uuid-2"]},
            uuid_solicitacao_acerto="uuid-solicitacao",
        )

        assert ctx.is_create is True
        assert ctx.valor_total == Decimal("150.5")
        assert ctx.valor_recursos_proprios == Decimal("10")
        assert ctx.valor_original == Decimal("150.50")
        assert ctx.retem_imposto is True
        assert ctx.eh_despesa_reconhecida_pela_associacao is False
        assert ctx.numero_boletim_de_ocorrencia == "BO-1"
        assert ctx.eh_despesa_sem_comprovacao_fiscal is True
        assert ctx.tipo_documento == "tipo-doc"
        assert ctx.tipo_transacao == "tipo-transacao"
        assert ctx.numero_documento == "123456"
        assert ctx.documento_transacao == "doc-transacao"
        assert ctx.cpf_cnpj_fornecedor == "11.478.276/0001-04"
        assert ctx.nome_fornecedor == "Fornecedor SA"
        assert ctx.rateios == ["rateio-1"]
        assert ctx.rateios_raw == ["uuid-1", "uuid-2"]
        assert ctx.despesas_impostos == ["imposto-1"]
        assert ctx.motivos_pagamento_antecipado == ["motivo-1"]
        assert ctx.outros_motivos == "outro motivo"
        assert ctx.associacao == "associacao-1"
        assert ctx.recurso is recurso
        assert ctx.despesa_instance is None
        assert ctx.uuid_solicitacao_acerto == "uuid-solicitacao"
        assert ctx.is_acerto is True

    def test_build_initial_data_none_resulta_em_rateios_raw_vazio(self):
        ctx = DespesaContextBuilder.build(validated_data={}, initial_data=None)

        assert ctx.rateios_raw == []


class TestBuildUpdate:
    def test_build_update_sem_validated_data_usa_a_instancia(self):
        instancia = _instancia_despesa()

        ctx = DespesaContextBuilder.build(validated_data={}, instance=instancia)

        assert ctx.is_create is False
        assert ctx.despesa_instance is instancia
        assert ctx.valor_total == instancia.valor_total
        assert ctx.valor_recursos_proprios == instancia.valor_recursos_proprios
        assert ctx.valor_original == instancia.valor_original
        assert ctx.retem_imposto is True
        assert ctx.eh_despesa_reconhecida_pela_associacao is True
        assert ctx.numero_boletim_de_ocorrencia == "BO-1"
        assert ctx.eh_despesa_sem_comprovacao_fiscal is True
        assert ctx.tipo_documento == "tipo-doc-instancia"
        assert ctx.tipo_transacao == "tipo-transacao-instancia"
        assert ctx.numero_documento == "999"
        assert ctx.documento_transacao == "doc-transacao-instancia"
        assert ctx.cpf_cnpj_fornecedor == "11.478.276/0001-04"
        assert ctx.nome_fornecedor == "Fornecedor da instância"
        assert ctx.rateios == ["rateio-instancia"]
        assert ctx.despesas_impostos == ["imposto-instancia"]
        assert ctx.motivos_pagamento_antecipado == ["motivo-instancia"]
        assert ctx.outros_motivos == "outro motivo da instância"
        assert ctx.associacao == "associacao-instancia"

    def test_build_update_recurso_nao_vem_da_instancia(self):
        """recurso é parâmetro externo (self.context no serializer), não é lido da instância."""
        instancia = _instancia_despesa()

        ctx = DespesaContextBuilder.build(validated_data={}, instance=instancia)

        assert ctx.recurso is None

    def test_build_validated_data_tem_precedencia_sobre_a_instancia(self):
        instancia = _instancia_despesa(numero_documento="999")

        ctx = DespesaContextBuilder.build(
            validated_data={"numero_documento": "123456"},
            instance=instancia,
        )

        assert ctx.numero_documento == "123456"

    def test_build_chave_none_em_validated_data_nao_recai_para_a_instancia(self):
        """Se a chave está presente em validated_data (mesmo com valor None), o builder não
        consulta a instância.

        Comportamento esperado: a edição de despesa é feita via PUT (validated_data sempre
        completo), então um campo None em validated_data é uma limpeza intencional do valor,
        não uma omissão que devesse herdar o dado da instância (PATCH)."""
        instancia = _instancia_despesa(numero_documento="999")

        ctx = DespesaContextBuilder.build(
            validated_data={"numero_documento": None},
            instance=instancia,
        )

        assert ctx.numero_documento == ""

    def test_build_reconhecida_false_na_instancia_nao_e_sobrescrita_para_true(self):
        instancia = _instancia_despesa(eh_despesa_reconhecida_pela_associacao=False)

        ctx = DespesaContextBuilder.build(validated_data={}, instance=instancia)

        assert ctx.eh_despesa_reconhecida_pela_associacao is False

    def test_build_instancia_sem_valor_original_fica_none(self):
        instancia = SimpleNamespace()

        ctx = DespesaContextBuilder.build(validated_data={}, instance=instancia)

        assert ctx.valor_original is None


class TestBuildCamposComRegrasEspeciais:
    def test_build_reconhecida_explicita_false_e_preservada(self):
        ctx = DespesaContextBuilder.build(
            validated_data={"eh_despesa_reconhecida_pela_associacao": False}
        )

        assert ctx.eh_despesa_reconhecida_pela_associacao is False

    def test_build_retem_imposto_truthy_e_convertido_para_bool(self):
        ctx = DespesaContextBuilder.build(validated_data={"retem_imposto": 1})

        assert ctx.retem_imposto is True

    def test_build_outros_motivos_mantem_string_vazia_explicita(self):
        ctx = DespesaContextBuilder.build(
            validated_data={"outros_motivos_pagamento_antecipado": ""}
        )

        assert ctx.outros_motivos == ""

    def test_build_valor_original_ausente_fica_none(self):
        ctx = DespesaContextBuilder.build(validated_data={"valor_total": 100})

        assert ctx.valor_original is None
