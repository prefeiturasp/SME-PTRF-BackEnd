from datetime import date

import pytest
from freezegun import freeze_time

from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import PeriodoPaa

pytestmark = pytest.mark.django_db

HOJE = date(2026, 10, 28)


@pytest.fixture
def periodo_encerrado(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2025', data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))


@pytest.fixture
def periodo_vigente_2026(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))


@pytest.fixture
def periodo_proxima_vigencia(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 8, 1), data_final=date(2027, 12, 31))


@pytest.fixture
def periodo_mais_distante(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2028', data_inicial=date(2028, 8, 1), data_final=date(2028, 12, 31))


class TestVigenteEm:

    def test_ano_corrente_retorna_periodo_com_data_inicial_no_ano(
            self, periodo_encerrado, periodo_vigente_2026, periodo_proxima_vigencia):
        assert PeriodoPaa.vigente_em(HOJE) == periodo_vigente_2026

    def test_sem_periodo_no_ano_retorna_none(self, periodo_encerrado, periodo_proxima_vigencia):
        assert PeriodoPaa.vigente_em(HOJE) is None

    def test_janela_de_datas_considera_periodo_que_contem_a_data(
            self, monkeypatch, periodo_encerrado, periodo_vigente_2026, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'CRITERIO_PERIODO_VIGENTE', constantes.CRITERIO_PERIODO_VIGENTE_JANELA_DE_DATAS)

        assert PeriodoPaa.vigente_em(HOJE) == periodo_vigente_2026
        assert PeriodoPaa.vigente_em(date(2027, 4, 30)) == periodo_vigente_2026
        assert PeriodoPaa.vigente_em(date(2027, 5, 1)) is None

    def test_criterios_divergem_com_periodos_menores_que_um_ano(
            self, monkeypatch, periodo_paa_factory):
        semestre_1 = periodo_paa_factory.create(
            referencia='2025.1', data_inicial=date(2025, 2, 1), data_final=date(2025, 7, 31))
        semestre_2 = periodo_paa_factory.create(
            referencia='2025.2', data_inicial=date(2025, 8, 1), data_final=date(2025, 12, 31))
        hoje = date(2025, 10, 28)

        monkeypatch.setattr(
            constantes, 'CRITERIO_PERIODO_VIGENTE', constantes.CRITERIO_PERIODO_VIGENTE_ANO_CORRENTE)
        assert PeriodoPaa.vigente_em(hoje) == semestre_1

        monkeypatch.setattr(
            constantes, 'CRITERIO_PERIODO_VIGENTE', constantes.CRITERIO_PERIODO_VIGENTE_JANELA_DE_DATAS)
        assert PeriodoPaa.vigente_em(hoje) == semestre_2


class TestProximaVigenciaEm:

    def test_retorna_primeiro_periodo_apos_o_fim_do_vigente(
            self, periodo_vigente_2026, periodo_proxima_vigencia, periodo_mais_distante):
        assert PeriodoPaa.proxima_vigencia_em(HOJE) == periodo_proxima_vigencia

    def test_sem_vigente_retorna_primeiro_periodo_apos_a_data(
            self, periodo_encerrado, periodo_proxima_vigencia, periodo_mais_distante):
        assert PeriodoPaa.proxima_vigencia_em(HOJE) == periodo_proxima_vigencia

    def test_sem_periodo_posterior_retorna_none(self, periodo_encerrado, periodo_vigente_2026):
        assert PeriodoPaa.proxima_vigencia_em(HOJE) is None


class TestPeriodoVigente:

    @freeze_time('2026-10-28')
    def test_delega_para_vigente_em(self, periodo_vigente_2026, periodo_proxima_vigencia):
        assert PeriodoPaa.periodo_vigente() == periodo_vigente_2026


class TestRelevantesPara:

    def test_retorna_vigente_e_proxima_vigencia_imediata(
            self, paa_factory, periodo_encerrado, periodo_vigente_2026,
            periodo_proxima_vigencia, periodo_mais_distante):
        paa = paa_factory.create(periodo_paa=periodo_vigente_2026)

        periodos = list(PeriodoPaa.relevantes_para(paa.associacao, HOJE))

        assert periodos == [periodo_vigente_2026, periodo_proxima_vigencia]

    def test_inclui_encerrado_com_paa_da_associacao_em_elaboracao(
            self, paa_factory, periodo_encerrado, periodo_vigente_2026, periodo_proxima_vigencia):
        paa = paa_factory.create(periodo_paa=periodo_encerrado, status=PaaStatusEnum.EM_ELABORACAO.name)

        periodos = list(PeriodoPaa.relevantes_para(paa.associacao, HOJE))

        assert periodos == [periodo_encerrado, periodo_vigente_2026, periodo_proxima_vigencia]

    def test_nao_inclui_encerrado_com_paa_de_outra_associacao(
            self, paa_factory, associacao_factory, periodo_encerrado, periodo_vigente_2026):
        paa_factory.create(periodo_paa=periodo_encerrado, status=PaaStatusEnum.EM_ELABORACAO.name)
        outra_associacao = associacao_factory.create()

        periodos = list(PeriodoPaa.relevantes_para(outra_associacao, HOJE))

        assert periodo_encerrado not in periodos

    def test_nao_inclui_encerrado_sem_paa_ou_com_paa_gerado(
            self, paa_factory, periodo_paa_factory, periodo_vigente_2026):
        gerado = periodo_paa_factory.create(
            referencia='2024', data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
        sem_paa = periodo_paa_factory.create(
            referencia='2023', data_inicial=date(2023, 1, 1), data_final=date(2023, 12, 31))
        paa = paa_factory.create(periodo_paa=gerado, status=PaaStatusEnum.GERADO.name)

        periodos = list(PeriodoPaa.relevantes_para(paa.associacao, HOJE))

        assert gerado not in periodos
        assert sem_paa not in periodos

    def test_sem_duplicidade_com_varios_paas_no_periodo(
            self, paa_factory, associacao_factory, periodo_encerrado, periodo_vigente_2026):
        paa = paa_factory.create(periodo_paa=periodo_encerrado, status=PaaStatusEnum.EM_ELABORACAO.name)
        paa_factory.create(
            periodo_paa=periodo_encerrado, associacao=associacao_factory.create(),
            status=PaaStatusEnum.EM_ELABORACAO.name)

        periodos = list(PeriodoPaa.relevantes_para(paa.associacao, HOJE))

        assert periodos.count(periodo_encerrado) == 1
