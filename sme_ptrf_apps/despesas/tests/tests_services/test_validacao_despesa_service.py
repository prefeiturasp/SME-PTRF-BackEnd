import pytest
from datetime import date
from rest_framework import serializers

from sme_ptrf_apps.despesas.services.validacao_despesa_service import (
    ValidacaoDespesaService
)
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import (
    APLICACAO_CUSTEIO,
    APLICACAO_CAPITAL
)


@pytest.fixture
def conta_ativa():
    class ContaFake:
        data_inicio = date(2024, 1, 1)
        data_encerramento = None

    return ContaFake()


@pytest.fixture
def conta_encerrada():
    class ContaFake:
        data_inicio = date(2023, 1, 1)
        data_encerramento = date(2024, 1, 31)

    return ContaFake()


def test_validar_rateios_serializer_ok():
    rateios = [
        {
            "valor_rateio": 100,
            "aplicacao_recurso": APLICACAO_CUSTEIO,
        }
    ]

    ValidacaoDespesaService.validar_rateios_serializer(
        valor_total=100,
        raw_rateios=rateios,
        raw_despesas_impostos=[],
        retem_imposto=False,
        valor_recursos_proprios=0,
    )


def test_validar_rateios_serializer_sem_rateios():
    with pytest.raises(serializers.ValidationError) as exc:
        ValidacaoDespesaService.validar_rateios_serializer(
            valor_total=100,
            raw_rateios=[],
        )

    assert "ao menos um rateio" in str(exc.value)


def test_validar_rateios_serializer_soma_invalida():
    rateios = [
        {"valor_rateio": 80, "aplicacao_recurso": APLICACAO_CUSTEIO},
    ]

    with pytest.raises(serializers.ValidationError) as exc:
        ValidacaoDespesaService.validar_rateios_serializer(
            valor_total=100,
            raw_rateios=rateios,
        )

    assert "soma dos rateios" in str(exc.value)


def test_rateio_capital_quantidade_zero():
    rateios = [
        {
            "valor_rateio": 100,
            "aplicacao_recurso": APLICACAO_CAPITAL,
            "quantidade_itens_capital": 0,
            "valor_item_capital": 50,
        }
    ]

    with pytest.raises(serializers.ValidationError) as exc:
        ValidacaoDespesaService.validar_rateios_serializer(
            valor_total=100,
            raw_rateios=rateios,
        )

    assert "quantidade menor ou igual a zero" in str(exc.value)


def test_rateio_capital_valor_divergente():
    rateios = [
        {
            "valor_rateio": 100,
            "aplicacao_recurso": APLICACAO_CAPITAL,
            "quantidade_itens_capital": 2,
            "valor_item_capital": 40,
        }
    ]

    with pytest.raises(serializers.ValidationError) as exc:
        ValidacaoDespesaService.validar_rateios_serializer(
            valor_total=100,
            raw_rateios=rateios,
        )

    assert "diverge do valor calculado" in str(exc.value)


@pytest.mark.django_db
def test_validar_conta_rateio_inicio_maior(conta_ativa):
    rateios = [
        {"conta_associacao": conta_ativa}
    ]

    conta_ativa.data_inicio = date(2025, 1, 10)

    with pytest.raises(serializers.ValidationError) as exc:
        ValidacaoDespesaService.validar_periodo_e_contas(
            instance=None,
            data_transacao=date(2025, 1, 5),
            rateios=rateios,
            despesas_impostos=[],
        )

    assert "data de início posterior" in str(exc.value)


@pytest.mark.django_db
def test_validar_conta_rateio_encerrada(conta_encerrada):
    rateios = [
        {"conta_associacao": conta_encerrada}
    ]

    with pytest.raises(serializers.ValidationError) as exc:
        ValidacaoDespesaService.validar_periodo_e_contas(
            instance=None,
            data_transacao=date(2025, 2, 1),
            rateios=rateios,
            despesas_impostos=[],
        )

    assert "data de encerramento anterior" in str(exc.value)


@pytest.mark.django_db
def test_validar_conta_imposto_inicio_maior(conta_ativa):
    conta_ativa.data_inicio = date(2025, 2, 1)

    despesas_impostos = [
        {
            "data_transacao": date(2025, 1, 15),
            "rateios": [
                {"conta_associacao": conta_ativa}
            ]
        }
    ]

    with pytest.raises(serializers.ValidationError) as exc:
        ValidacaoDespesaService.validar_periodo_e_contas(
            instance=None,
            data_transacao=date(2025, 1, 15),
            rateios=[],
            despesas_impostos=despesas_impostos,
        )

    assert "rateios de imposto" in str(exc.value)
