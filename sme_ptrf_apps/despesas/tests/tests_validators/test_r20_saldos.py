from datetime import date
from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.r20_saldos import SaldosValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return SaldosValidator()


def test_valida_ok_sempre_passthrough(validator):
    # considerar_na_pipeline=False → retorna ctx imediatamente sem qualquer verificação
    ctx = make_ctx()
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_passthrough_com_associacao_e_data(validator):
    ctx = make_ctx(
        associacao=SimpleNamespace(uuid="alguma-uuid"),
        data_transacao=date(2020, 3, 10),
    )
    result = validator.validate(ctx)
    assert result is ctx


class TestGarantirUuids:
    """A regra em si está desativada (validate() é passthrough), mas _garantir_uuids
    é um utilitário público independente — testado isoladamente aqui."""

    def test_lista_vazia_retorna_lista_vazia(self):
        assert SaldosValidator._garantir_uuids([]) == []

    def test_converte_instancias_de_model_para_uuid_string(self):
        conta = SimpleNamespace(uuid="uuid-conta")
        acao = SimpleNamespace(uuid="uuid-acao")
        rateios = [{"conta_associacao": conta, "acao_associacao": acao, "valor_rateio": 100}]

        resultado = SaldosValidator._garantir_uuids(rateios)

        assert resultado == [
            {"conta_associacao": "uuid-conta", "acao_associacao": "uuid-acao", "valor_rateio": 100}
        ]

    def test_mantem_valor_ja_string_inalterado(self):
        rateios = [{"conta_associacao": "uuid-ja-string", "acao_associacao": "uuid-acao-string"}]

        resultado = SaldosValidator._garantir_uuids(rateios)

        assert resultado == [{"conta_associacao": "uuid-ja-string", "acao_associacao": "uuid-acao-string"}]

    def test_ignora_campos_ausentes(self):
        rateios = [{"valor_rateio": 50}]

        resultado = SaldosValidator._garantir_uuids(rateios)

        assert resultado == [{"valor_rateio": 50}]

    def test_ignora_valor_none(self):
        rateios = [{"conta_associacao": None, "acao_associacao": None}]

        resultado = SaldosValidator._garantir_uuids(rateios)

        assert resultado == [{"conta_associacao": None, "acao_associacao": None}]

    def test_converte_apenas_o_campo_que_e_instancia_de_model(self):
        conta = SimpleNamespace(uuid="uuid-conta")
        rateios = [{"conta_associacao": conta, "acao_associacao": "uuid-acao-ja-string"}]

        resultado = SaldosValidator._garantir_uuids(rateios)

        assert resultado == [{"conta_associacao": "uuid-conta", "acao_associacao": "uuid-acao-ja-string"}]

    def test_processa_multiplos_rateios_preservando_a_ordem(self):
        conta_1 = SimpleNamespace(uuid="uuid-conta-1")
        conta_2 = SimpleNamespace(uuid="uuid-conta-2")
        rateios = [
            {"conta_associacao": conta_1, "id": 1},
            {"conta_associacao": conta_2, "id": 2},
        ]

        resultado = SaldosValidator._garantir_uuids(rateios)

        assert [r["conta_associacao"] for r in resultado] == ["uuid-conta-1", "uuid-conta-2"]
        assert [r["id"] for r in resultado] == [1, 2]

    def test_nao_muta_o_dict_original(self):
        conta = SimpleNamespace(uuid="uuid-conta")
        rateio_original = {"conta_associacao": conta}

        SaldosValidator._garantir_uuids([rateio_original])

        assert rateio_original["conta_associacao"] is conta
