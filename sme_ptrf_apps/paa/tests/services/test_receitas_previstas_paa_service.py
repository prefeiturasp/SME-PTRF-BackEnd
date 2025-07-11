import pytest
from freezegun import freeze_time
from datetime import datetime
from sme_ptrf_apps.paa.services.receitas_previstas_paa_service import SaldosPorAcaoPaaService


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
