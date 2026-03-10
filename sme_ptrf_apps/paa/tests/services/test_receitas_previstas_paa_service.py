import pytest
from freezegun import freeze_time
from datetime import datetime
from unittest.mock import patch, MagicMock
from sme_ptrf_apps.paa.services.receitas_previstas_paa_service import SaldosPorAcaoPaaService
from sme_ptrf_apps.paa.services import ValidacaoSaldoIndisponivel
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum


@pytest.mark.django_db
@freeze_time("2025-01-01")
def test_congelar_saldos(paa_factory, acao_associacao_factory, periodo_paa_2025_1):
    paa = paa_factory.create(periodo_paa=periodo_paa_2025_1)

    acao_associacao_factory.create(associacao=paa.associacao)
    acao_associacao_factory.create(associacao=paa.associacao)

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)
    receitas_previstas = service.congelar_saldos()

    assert paa.saldo_congelado_em == datetime(2025, 1, 1)
    assert len(receitas_previstas) == 2

    for receita in receitas_previstas:
        assert receita.paa == paa
        assert receita.saldo_congelado_custeio is not None
        assert receita.saldo_congelado_capital is not None
        assert receita.saldo_congelado_livre is not None


@pytest.mark.django_db
def test_congelar_saldos_ja_congelado(paa_factory, periodo_paa_2025_1):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_2025_1,
        saldo_congelado_em="2025-01-01"
    )

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)
    receitas_previstas = service.congelar_saldos()

    assert receitas_previstas == []


@pytest.mark.django_db
def test_descongelar_saldos(paa_factory, acao_associacao_factory, receita_prevista_paa_factory, periodo_paa_2025_1):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_2025_1,
        saldo_congelado_em="2025-01-01"
    )

    acao1 = acao_associacao_factory.create(associacao=paa.associacao)
    acao2 = acao_associacao_factory.create(associacao=paa.associacao)

    receita_prevista_paa_factory.create(
        paa=paa,
        acao_associacao=acao1,
        saldo_congelado_custeio=100,
        saldo_congelado_capital=50,
        saldo_congelado_livre=20
    )
    receita_prevista_paa_factory.create(
        paa=paa,
        acao_associacao=acao2,
        saldo_congelado_custeio=200,
        saldo_congelado_capital=100,
        saldo_congelado_livre=40
    )

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)
    receitas_previstas = service.descongelar_saldos()

    assert paa.saldo_congelado_em is None
    for receita in receitas_previstas:
        assert receita.saldo_congelado_custeio is None
        assert receita.saldo_congelado_capital is None
        assert receita.saldo_congelado_livre is None


def test_limpar_prioridades_impactadas_despesas_delega_ao_service_correto():
    """Verifica que o método delega para PrioridadesPaaImpactadasReceitasPrevistasPTRFService
    com os argumentos corretos: dict vazio e a instância de receita_prevista."""
    paa_mock = MagicMock()
    service = SaldosPorAcaoPaaService(paa=paa_mock, associacao=paa_mock.associacao)
    receita_prevista_mock = MagicMock()

    with patch(
        "sme_ptrf_apps.paa.services.PrioridadesPaaImpactadasReceitasPrevistasPTRFService"
    ) as MockService:
        mock_instance = MockService.return_value
        service._limpar_prioridades_impactadas_despesas(receita_prevista_mock)

    MockService.assert_called_once_with({}, receita_prevista_mock)
    mock_instance.limpar_valor_prioridades_saldo_indisponivel_da_acao_receita.assert_called_once()


@pytest.mark.django_db
def test_limpar_prioridades_impactadas_despesas_sem_prioridades_retorna_vazio(
    paa_factory, acao_associacao_factory, receita_prevista_paa_factory, periodo_paa_2025_1
):
    """Quando não há prioridades vinculadas à receita prevista,
    o método não altera nenhum registro e retorna lista vazia."""
    paa = paa_factory.create(periodo_paa=periodo_paa_2025_1)
    acao = acao_associacao_factory.create(associacao=paa.associacao)
    receita_prevista = receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao)

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)

    with patch(
        "sme_ptrf_apps.paa.services.resumo_prioridades_service"
        ".ResumoPrioridadesService.validar_valor_prioridade"
    ):
        resultado = service._limpar_prioridades_impactadas_despesas(receita_prevista)

    assert resultado is None or resultado == []


@pytest.mark.django_db
def test_limpar_prioridades_impactadas_despesas_prioridades_saldo_indisponivel_sao_limpas(
    paa_factory, acao_associacao_factory, receita_prevista_paa_factory,
    prioridade_paa_factory, periodo_paa_2025_1
):
    """Quando há prioridades cujo saldo se torna indisponível (ValidacaoSaldoIndisponivel),
    o campo valor_total dessas prioridades é definido como None."""
    paa = paa_factory.create(periodo_paa=periodo_paa_2025_1)
    acao = acao_associacao_factory.create(associacao=paa.associacao)
    receita_prevista = receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao)

    prioridade = prioridade_paa_factory.create(
        paa=paa,
        acao_associacao=acao,
        recurso=RecursoOpcoesEnum.PTRF.name,
        tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        acao_pdde=None,
        programa_pdde=None,
        valor_total=500,
    )

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)

    with patch(
        "sme_ptrf_apps.paa.services.resumo_prioridades_service"
        ".ResumoPrioridadesService.validar_valor_prioridade",
        side_effect=ValidacaoSaldoIndisponivel("Saldo insuficiente")
    ):
        service._limpar_prioridades_impactadas_despesas(receita_prevista)

    prioridade.refresh_from_db()
    assert prioridade.valor_total is None


@pytest.mark.django_db
def test_limpar_prioridades_impactadas_despesas_prioridades_saldo_disponivel_nao_sao_limpas(
    paa_factory, acao_associacao_factory, receita_prevista_paa_factory,
    prioridade_paa_factory, periodo_paa_2025_1
):
    """Quando o saldo permanece disponível, o campo valor_total das prioridades
    não deve ser alterado."""
    paa = paa_factory.create(periodo_paa=periodo_paa_2025_1)
    acao = acao_associacao_factory.create(associacao=paa.associacao)
    receita_prevista = receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao)

    prioridade = prioridade_paa_factory.create(
        paa=paa,
        acao_associacao=acao,
        recurso=RecursoOpcoesEnum.PTRF.name,
        tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        acao_pdde=None,
        programa_pdde=None,
        valor_total=500,
    )

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)

    with patch(
        "sme_ptrf_apps.paa.services.resumo_prioridades_service"
        ".ResumoPrioridadesService.validar_valor_prioridade"
    ):
        service._limpar_prioridades_impactadas_despesas(receita_prevista)

    prioridade.refresh_from_db()
    assert prioridade.valor_total == 500


@pytest.mark.django_db
def test_limpar_prioridades_impactadas_despesas_somente_prioridades_da_acao_sao_impactadas(
    paa_factory, acao_associacao_factory, receita_prevista_paa_factory,
    prioridade_paa_factory, periodo_paa_2025_1
):
    """Prioridades de outras ações não devem ser afetadas pelo método,
    mesmo que o saldo da ação da receita prevista seja indisponível."""
    paa = paa_factory.create(periodo_paa=periodo_paa_2025_1)
    acao_alvo = acao_associacao_factory.create(associacao=paa.associacao)
    acao_outra = acao_associacao_factory.create(associacao=paa.associacao)
    receita_prevista = receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao_alvo)

    prioridade_alvo = prioridade_paa_factory.create(
        paa=paa,
        acao_associacao=acao_alvo,
        recurso=RecursoOpcoesEnum.PTRF.name,
        tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        acao_pdde=None,
        programa_pdde=None,
        valor_total=300,
    )
    prioridade_outra = prioridade_paa_factory.create(
        paa=paa,
        acao_associacao=acao_outra,
        recurso=RecursoOpcoesEnum.PTRF.name,
        tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        acao_pdde=None,
        programa_pdde=None,
        valor_total=400,
    )

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)

    with patch(
        "sme_ptrf_apps.paa.services.resumo_prioridades_service"
        ".ResumoPrioridadesService.validar_valor_prioridade",
        side_effect=ValidacaoSaldoIndisponivel("Saldo insuficiente")
    ):
        service._limpar_prioridades_impactadas_despesas(receita_prevista)

    prioridade_alvo.refresh_from_db()
    prioridade_outra.refresh_from_db()
    assert prioridade_alvo.valor_total is None
    assert prioridade_outra.valor_total == 400


@pytest.mark.django_db
def test_limpar_prioridades_impactadas_despesas_prioridade_com_valor_total_none_ignorada(
    paa_factory, acao_associacao_factory, receita_prevista_paa_factory,
    prioridade_paa_factory, periodo_paa_2025_1
):
    """Prioridades cujo valor_total já é None são ignoradas pelo método
    (filtro valor_total__isnull=False na query base)."""
    paa = paa_factory.create(periodo_paa=periodo_paa_2025_1)
    acao = acao_associacao_factory.create(associacao=paa.associacao)
    receita_prevista = receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao)

    prioridade = prioridade_paa_factory.create(
        paa=paa,
        acao_associacao=acao,
        recurso=RecursoOpcoesEnum.PTRF.name,
        tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        acao_pdde=None,
        programa_pdde=None,
        valor_total=None,
    )

    service = SaldosPorAcaoPaaService(paa=paa, associacao=paa.associacao)

    mock_validar = MagicMock()
    with patch(
        "sme_ptrf_apps.paa.services.resumo_prioridades_service"
        ".ResumoPrioridadesService.validar_valor_prioridade",
        mock_validar
    ):
        service._limpar_prioridades_impactadas_despesas(receita_prevista)

    mock_validar.assert_not_called()
    prioridade.refresh_from_db()
    assert prioridade.valor_total is None
