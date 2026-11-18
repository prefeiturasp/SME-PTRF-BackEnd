"""Trava de segurança: dados legados com períodos sobrepostos não podem gerar decisões ambíguas."""
from datetime import date

import pytest

from sme_ptrf_apps.paa.models import PeriodoPaa
from sme_ptrf_apps.paa.services import VigenciaElaboracaoPaaService
from sme_ptrf_apps.paa.services.elaboracao_paa_service import (
    ElaboracaoPaaService, PeriodoInvalidoParaElaboracaoException)

pytestmark = pytest.mark.django_db

HOJE = date(2026, 10, 28)


@pytest.fixture
def vigente(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))


def test_sem_sobreposicao_nao_aciona_a_trava(vigente, periodo_paa_factory):
    periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 5, 1), data_final=date(2027, 12, 31))

    assert PeriodoPaa.tem_sobreposicao_relevante(HOJE) is False


def test_periodo_sobreposto_ao_vigente_aciona_a_trava(vigente, periodo_paa_factory):
    periodo_paa_factory.create(
        referencia='2026 teste', data_inicial=date(2026, 11, 1), data_final=date(2026, 12, 31))

    assert PeriodoPaa.tem_sobreposicao_relevante(HOJE) is True


def test_sobreposicao_alheia_ao_vigente_e_a_proxima_vigencia_nao_aciona(vigente, periodo_paa_factory):
    periodo_paa_factory.create(
        referencia='2024 a', data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_paa_factory.create(
        referencia='2024 b', data_inicial=date(2024, 6, 1), data_final=date(2024, 8, 31))

    assert PeriodoPaa.tem_sobreposicao_relevante(HOJE) is False


def test_vigencia_sinaliza_periodos_sobrepostos(associacao, vigente, periodo_paa_factory, parametro_paa_factory):
    parametro_paa_factory.create(mes_elaboracao_paa=10)
    periodo_paa_factory.create(
        referencia='2026 teste', data_inicial=date(2026, 11, 1), data_final=date(2026, 12, 31))

    vigencia = VigenciaElaboracaoPaaService.obter(associacao, True, hoje=HOJE)

    assert vigencia['periodos_sobrepostos'] is True


def test_criacao_e_recusada_com_periodos_sobrepostos(
        associacao, vigente, periodo_paa_factory, parametro_paa_factory):
    parametro_paa_factory.create(mes_elaboracao_paa=10)
    periodo_paa_factory.create(
        referencia='2026 teste', data_inicial=date(2026, 11, 1), data_final=date(2026, 12, 31))

    with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='sobrepostos'):
        ElaboracaoPaaService.validar_periodo_para_criacao(associacao, vigente, True, hoje=HOJE)
