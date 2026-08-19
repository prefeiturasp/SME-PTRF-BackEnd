
import pytest
from datetime import date
from decimal import Decimal

from sme_ptrf_apps.core.services.info_por_acao_services import (
    info_conta_associacao_no_periodo,
    info_acao_associacao_no_periodo
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def dados_fechamento_conta(
    associacao_factory,
    conta_associacao_factory,
    periodo_factory,
    fechamento_periodo_factory,
    prestacao_conta_factory,
    acao_associacao_factory,
    acao_factory,
    tipo_conta_factory,
):
    associacao = associacao_factory.create()

    acao = acao_factory.create(
        nome="PTRF Básico",
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre=True,
    )
    acao_associacao = acao_associacao_factory.create(
        associacao=associacao,
        acao=acao,
    )

    tipo_conta = tipo_conta_factory.create(nome="Cheque")

    conta = conta_associacao_factory.create(
        tipo_conta=tipo_conta,
        associacao=associacao,
    )

    periodo_anterior = periodo_factory.create(
        referencia="2021.3",
        data_inicio_realizacao_despesas=date(2021, 10, 1),
        data_fim_realizacao_despesas=date(2021, 12, 31),   
    )

    # O valor está em receitas porque ele vai gerar no pre_save os saldo_programados
    fechamento_anterior = fechamento_periodo_factory.create(
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_custeio=6000,
        total_despesas_custeio=0,

        total_receitas_capital=0,
        total_receitas_livre=0,
        total_despesas_capital=0,

        status="FECHADO",
    )

    assert fechamento_anterior.saldo_reprogramado_custeio == Decimal("6000.00")

    periodo = periodo_factory.create(
        periodo_anterior=periodo_anterior,
        referencia="2022.1",
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 4, 30),
    )

    pc = prestacao_conta_factory.create(
        periodo=periodo,
        associacao=associacao,
    )
    '''
        saldo_anterior_custeio = fechamento_anterior.saldo_reprogramado_custeio
        saldo_anterior_capital = fechamento_anterior.saldo_reprogramado_capital
        saldo_anterior_livre = fechamento_anterior.saldo_reprogramado_livre
    '''
    fechamento = fechamento_periodo_factory.create(
        prestacao_conta=pc,
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_anterior,

        total_receitas_custeio=0,
        total_despesas_custeio=0,

        total_receitas_capital=0,
        total_despesas_capital=0,

        total_receitas_livre=0,

        status="FECHADO",
    )

    assert fechamento.saldo_anterior_custeio == Decimal("6000.00")

    return associacao, conta, acao_associacao, periodo



def test_info_conta_associacao_no_periodo_recalcula_saldo_com_rateios_atuais(
    dados_fechamento_conta,
    despesa_factory,
    rateio_despesa_factory,
):
    (
        associacao,
        conta,
        acao_associacao,
        periodo
    ) = dados_fechamento_conta

    # Despesas já cadastradas anteriormente
    despesa_antiga = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 1),
        data_documento=date(2022, 1, 1),
    )

    rateio_despesa_factory.create(
        despesa=despesa_antiga,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    # Despesa que se está editando
    despesa = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 2),
        data_documento=date(2022, 1, 2),
    )

    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    response = info_conta_associacao_no_periodo(
        conta_associacao=conta,
        periodo=periodo,
        exclude_despesa=str(despesa.uuid),
    )

    assert response["despesas_no_periodo_custeio"] == Decimal("1000.00")
    assert response["saldo_atual_custeio"] == Decimal("5000.00")


def test_info_acao_associacao_no_periodo_recalcula_saldo_com_rateios_atuais(
    dados_fechamento_conta,
    despesa_factory,
    rateio_despesa_factory,
):
    (
        associacao,
        conta,
        acao_associacao,
        periodo
    ) = dados_fechamento_conta

    # Despesas já cadastradas anteriormente
    despesa_antiga = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 1),
        data_documento=date(2022, 1, 1),
    )

    rateio_despesa_factory.create(
        despesa=despesa_antiga,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    # Despesa que se está editando
    despesa = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 2),
        data_documento=date(2022, 1, 2),
    )

    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    response = info_acao_associacao_no_periodo(
        acao_associacao=acao_associacao,
        periodo=periodo,
        conta=conta,
        exclude_despesa=str(despesa.uuid),
    )

    assert response["despesas_no_periodo_custeio"] == Decimal("1000.00")
    assert response["saldo_atual_custeio"] == Decimal("5000.00")


def test_info_conta_associacao_no_periodo_recalcula_saldo_com_rateios_atuais_sem_exclude(
    dados_fechamento_conta,
    despesa_factory,
    rateio_despesa_factory,
):
    (
        associacao,
        conta,
        acao_associacao,
        periodo
    ) = dados_fechamento_conta

    # Despesas já cadastradas anteriormente
    despesa_antiga = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 1),
        data_documento=date(2022, 1, 1),
    )

    rateio_despesa_factory.create(
        despesa=despesa_antiga,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    despesa = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 2),
        data_documento=date(2022, 1, 2),
    )
    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    response = info_conta_associacao_no_periodo(
        conta_associacao=conta,
        periodo=periodo,
    )

    assert response["despesas_no_periodo_custeio"] == Decimal("0")
    assert response["saldo_atual_custeio"] == Decimal("6000.00")


def test_info_acao_associacao_no_periodo_recalcula_saldo_com_rateios_atuais_sem_exclude(
    dados_fechamento_conta,
    despesa_factory,
    rateio_despesa_factory,
):
    (
        associacao,
        conta,
        acao_associacao,
        periodo
    ) = dados_fechamento_conta

    # Despesas já cadastradas anteriormente
    despesa_antiga = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 1),
        data_documento=date(2022, 1, 1),
    )

    rateio_despesa_factory.create(
        despesa=despesa_antiga,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    despesa = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2022, 1, 2),
        data_documento=date(2022, 1, 2),
    )

    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=Decimal("1000.00"),
        valor_original=Decimal("1000.00"),
        status="COMPLETO",
        conferido=True,
    )

    response = info_acao_associacao_no_periodo(
        acao_associacao=acao_associacao,
        periodo=periodo,
        conta=conta,
       
    )
    assert response["despesas_no_periodo_custeio"] == Decimal("0")
    assert response["saldo_atual_custeio"] == Decimal("6000.00")