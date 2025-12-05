from decimal import Decimal
import pytest

from datetime import date
from sme_ptrf_apps.core.services import saldos_insuficientes_para_rateios

pytestmark = pytest.mark.django_db


@pytest.fixture
def dados_em_comum_testes_saldos_insuficientes_para_rateios(associacao_factory, conta_associacao_factory, despesa_factory, rateio_despesa_factory, periodo_factory, fechamento_periodo_factory, tipo_conta_factory, prestacao_conta_factory, acao_associacao_factory, acao_factory):
    associacao = associacao_factory.create()

    acao = acao_factory.create(nome="PTRF Básico", aceita_capital=True, aceita_custeio=True, aceita_livre=True)
    acao_associacao = acao_associacao_factory.create(associacao=associacao, acao=acao)

    tipo_conta = tipo_conta_factory.create(nome="Caixa")
    conta = conta_associacao_factory.create(tipo_conta=tipo_conta, associacao=associacao)

    periodo_anterior = periodo_factory.create(
        referencia="2021",
        data_inicio_realizacao_despesas=date(2021, 10, 1),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )
    periodo = periodo_factory.create(
        periodo_anterior=periodo_anterior,
        referencia="2022",
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 4, 30),
    )

    despesa = despesa_factory.create(associacao=associacao, data_transacao=date(
        2022, 1, 1), data_documento=date(2022, 1, 1))

    pc = prestacao_conta_factory.create(periodo=periodo, associacao=associacao)

    fechamento_periodo_factory.create(
        prestacao_conta=pc,
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_custeio=2000,
        total_receitas_livre=10000,
        total_receitas_capital=10000,
        status="FECHADO",
    )

    return associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc


def test_valor_conta_insuficiente(
    dados_em_comum_testes_saldos_insuficientes_para_rateios,
    rateio_despesa_factory,
):
    (
        associacao,
        acao_associacao,
        conta,
        periodo,
        periodo_anterior,
        despesa,
        pc,
    ) = dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateio = rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal(25000),
        valor_original=Decimal(25000),
        status="COMPLETO",
        conferido=True,
    )

    rateios = [{
        "id": rateio.id,
        "despesa": despesa,
        "conta_associacao": conta.uuid,
        "acao_associacao": acao_associacao.uuid,
        "aplicacao_recurso": "CUSTEIO",
        "valor_rateio": Decimal(25000),
    }]

    response = saldos_insuficientes_para_rateios(
        rateios=rateios,
        periodo=periodo,
        exclude_despesa=despesa.uuid,
    )

    assert response["tipo_saldo"] == "CONTA"
    info = response["saldos_insuficientes"][0]

    assert info["conta"] == "Caixa"
    assert info["saldo_disponivel"] == Decimal(22000)
    assert info["total_rateios"] == Decimal(25000)


def test_valor_acao_insuficiente(
    dados_em_comum_testes_saldos_insuficientes_para_rateios,
    rateio_despesa_factory,
):
    (
        associacao,
        acao_associacao,
        conta,
        periodo,
        periodo_anterior,
        despesa,
        pc,
    ) = dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateio = rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal(16000),
        valor_original=Decimal(16000),
        status="COMPLETO",
        conferido=True,
    )

    rateios = [{
        "id": rateio.id,
        "despesa": despesa,
        "conta_associacao": conta.uuid,
        "acao_associacao": acao_associacao.uuid,
        "aplicacao_recurso": "CUSTEIO",
        "valor_rateio": Decimal(16000),
    }]

    response = saldos_insuficientes_para_rateios(
        rateios=rateios,
        periodo=periodo,
        exclude_despesa=despesa.uuid,
    )

    assert response["tipo_saldo"] == "ACAO"
    info = response["saldos_insuficientes"][0]

    assert info["conta"] == "Caixa"
    assert info["aplicacao"] == "CUSTEIO"
    assert info["saldo_disponivel"] == Decimal(12000)
    assert info["total_rateios"] == Decimal(16000)


def test_valor_aplicacao_insuficiente(
    dados_em_comum_testes_saldos_insuficientes_para_rateios,
    rateio_despesa_factory,
):
    (
        associacao,
        acao_associacao,
        conta,
        periodo,
        periodo_anterior,
        despesa,
        pc,
    ) = dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateio = rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CAPITAL",
        valor_rateio=Decimal(21000),
        valor_original=Decimal(21000),
        status="COMPLETO",
        conferido=True,
    )

    rateios = [{
        "id": rateio.id,
        "despesa": despesa,
        "conta_associacao": conta.uuid,
        "acao_associacao": acao_associacao.uuid,
        "aplicacao_recurso": "CAPITAL",
        "valor_rateio": Decimal(21000),
    }]

    response = saldos_insuficientes_para_rateios(
        rateios=rateios,
        periodo=periodo,
        exclude_despesa=despesa.uuid,
    )

    assert response["tipo_saldo"] == "ACAO"

    info = response["saldos_insuficientes"][0]

    assert info["conta"] == "Caixa"
    assert info["aplicacao"] == "CAPITAL"
    assert info["saldo_disponivel"] == Decimal(20000)
    assert info["total_rateios"] == Decimal(21000)


def test_nao_retornar_insuficiente_acao(
    dados_em_comum_testes_saldos_insuficientes_para_rateios,
    rateio_despesa_factory,
):
    associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc = \
        dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateios = []

    rateio_custeio = rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        valor_rateio=Decimal(4000),
        valor_original=Decimal(4000),
        aplicacao_recurso="CUSTEIO",
        acao_associacao=acao_associacao,
        status="COMPLETO",
        conferido=True
    )

    rateio_capital = rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        valor_rateio=Decimal(3000),
        valor_original=Decimal(3000),
        aplicacao_recurso="CAPITAL",
        acao_associacao=acao_associacao,
        status="COMPLETO",
        conferido=True
    )

    rateios.append({
        'id': rateio_custeio.id,
        'despesa': rateio_custeio.despesa,
        'conta_associacao': rateio_custeio.conta_associacao.uuid,
        'acao_associacao': rateio_custeio.acao_associacao.uuid,
        'aplicacao_recurso': rateio_custeio.aplicacao_recurso,
        'valor_rateio': rateio_custeio.valor_rateio
    })

    rateios.append({
        'id': rateio_capital.id,
        'despesa': rateio_capital.despesa,
        'conta_associacao': rateio_capital.conta_associacao.uuid,
        'acao_associacao': rateio_capital.acao_associacao.uuid,
        'aplicacao_recurso': rateio_capital.aplicacao_recurso,
        'valor_rateio': rateio_capital.valor_rateio
    })

    response = saldos_insuficientes_para_rateios(
        rateios=rateios,
        periodo=periodo,
        exclude_despesa=despesa.uuid
    )

    assert response['tipo_saldo'] == "ACAO"
    assert response['saldos_insuficientes'] == []


def test_uso_valor_livre_aplicacao_em_um_rateio_mas_insuficiente_para_o_outro(
    dados_em_comum_testes_saldos_insuficientes_para_rateios,
    rateio_despesa_factory,
):
    associacao, acao_associacao, conta, periodo, periodo_anterior, despesa, pc = \
        dados_em_comum_testes_saldos_insuficientes_para_rateios

    rateio_custeio = rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        valor_rateio=Decimal(16000),
        valor_original=Decimal(16000),
        aplicacao_recurso="CUSTEIO",
        acao_associacao=acao_associacao,
        status="COMPLETO",
        conferido="True",
    )

    rateio_capital = rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        valor_rateio=Decimal(6000),
        valor_original=Decimal(6000),
        aplicacao_recurso="CAPITAL",
        acao_associacao=acao_associacao,
        status="COMPLETO",
        conferido="True",
    )

    rateios = [
        {
            'id': r.id,
            'despesa': r.despesa,
            'conta_associacao': r.conta_associacao.uuid,
            'acao_associacao': r.acao_associacao.uuid,
            'aplicacao_recurso': r.aplicacao_recurso,
            'valor_rateio': r.valor_rateio,
        }
        for r in (rateio_custeio, rateio_capital)
    ]

    response = saldos_insuficientes_para_rateios(
        rateios=rateios,
        periodo=periodo,
        exclude_despesa=despesa.uuid,
    )

    assert len(response['saldos_insuficientes']) == 1

    item = response['saldos_insuficientes'][0]

    assert response['tipo_saldo'] == "ACAO"
    assert item['conta'] == "Caixa"
    assert item['aplicacao'] == "CUSTEIO"
    assert item['saldo_disponivel'] == Decimal(12000)
    assert item['total_rateios'] == Decimal(16000)
