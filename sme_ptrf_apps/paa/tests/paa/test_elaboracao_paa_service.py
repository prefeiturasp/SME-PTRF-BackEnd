from datetime import date

import pytest

from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa, ParametroPaa
from sme_ptrf_apps.paa.services.elaboracao_paa_service import (
    ElaboracaoPaaService, PeriodoInvalidoParaElaboracaoException)

pytestmark = pytest.mark.django_db

HOJE = date(2026, 10, 28)


@pytest.fixture
def periodo_vigente(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))


@pytest.fixture
def periodo_proxima_vigencia(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 8, 1), data_final=date(2027, 12, 31))


@pytest.fixture(autouse=True)
def parametro_outubro(parametro_paa_factory):
    return parametro_paa_factory.create(mes_elaboracao_paa=10)


def _valida(associacao, periodo, habilitada=True):
    ElaboracaoPaaService.validar_periodo_para_criacao(associacao, periodo, habilitada, hoje=HOJE)


def _paa_com_plano_gerado(paa_factory, documento_paa_factory, associacao, periodo):
    paa = paa_factory.create(periodo_paa=periodo, associacao=associacao)
    documento_paa_factory.create(
        paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)
    return paa


def test_periodo_vigente_no_mes_parametrizado_e_permitido(associacao, periodo_vigente):
    _valida(associacao, periodo_vigente)


def test_periodo_encerrado_e_recusado(associacao, periodo_paa_factory):
    encerrado = periodo_paa_factory.create(
        referencia='2025', data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='já foi encerrado'):
        _valida(associacao, encerrado)


class TestModoMesElaboracao:
    """HOJE é outubro (mês 10). O mês parametrizado varia por teste."""

    @pytest.fixture
    def modo_igual(self, monkeypatch):
        monkeypatch.setattr(constantes, 'MODO_MES_ELABORACAO', constantes.MES_ELABORACAO_IGUAL)

    @pytest.fixture
    def modo_a_partir_de(self, monkeypatch):
        monkeypatch.setattr(constantes, 'MODO_MES_ELABORACAO', constantes.MES_ELABORACAO_A_PARTIR_DE)

    @staticmethod
    def _mes_parametrizado(mes):
        ParametroPaa.objects.update(mes_elaboracao_paa=mes)

    @pytest.mark.usefixtures('modo_igual')
    def test_igual_libera_no_proprio_mes(self, associacao, periodo_vigente):
        self._mes_parametrizado(10)

        _valida(associacao, periodo_vigente)

    @pytest.mark.usefixtures('modo_igual')
    @pytest.mark.parametrize('mes_parametrizado', [9, 11])
    def test_igual_recusa_mes_anterior_ou_posterior(self, associacao, periodo_vigente, mes_parametrizado):
        self._mes_parametrizado(mes_parametrizado)

        with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='só pode ser iniciada no mês parametrizado'):
            _valida(associacao, periodo_vigente)

    @pytest.mark.usefixtures('modo_a_partir_de')
    @pytest.mark.parametrize('mes_parametrizado', [9, 10])
    def test_a_partir_de_libera_no_mes_parametrizado_e_depois_dele(
            self, associacao, periodo_vigente, mes_parametrizado):
        self._mes_parametrizado(mes_parametrizado)

        _valida(associacao, periodo_vigente)

    @pytest.mark.usefixtures('modo_a_partir_de')
    def test_a_partir_de_recusa_antes_do_mes_parametrizado(self, associacao, periodo_vigente):
        self._mes_parametrizado(11)

        with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='a partir do mês parametrizado'):
            _valida(associacao, periodo_vigente)

    def test_modo_desconhecido_e_erro_de_configuracao(self, monkeypatch, associacao, periodo_vigente):
        monkeypatch.setattr(constantes, 'MODO_MES_ELABORACAO', 'QUALQUER')

        with pytest.raises(ValueError, match='desconhecido'):
            _valida(associacao, periodo_vigente)

    def test_modo_padrao_e_igual(self):
        assert constantes.MODO_MES_ELABORACAO == constantes.MES_ELABORACAO_IGUAL


def test_periodo_fora_do_vigente_e_da_proxima_vigencia_e_recusado(
        associacao, periodo_vigente, periodo_proxima_vigencia, periodo_paa_factory):
    mais_distante = periodo_paa_factory.create(
        referencia='2028', data_inicial=date(2028, 8, 1), data_final=date(2028, 12, 31))

    with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='vigente ou da próxima vigência'):
        _valida(associacao, mais_distante)


class TestProximaVigencia:

    def test_permitida_com_vigente_gerado_parcialmente(
            self, paa_factory, documento_paa_factory, associacao, periodo_vigente, periodo_proxima_vigencia):
        _paa_com_plano_gerado(paa_factory, documento_paa_factory, associacao, periodo_vigente)

        _valida(associacao, periodo_proxima_vigencia)

    def test_permitida_com_vigente_gerado(
            self, paa_factory, documento_paa_factory, ata_paa_factory, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        paa = _paa_com_plano_gerado(paa_factory, documento_paa_factory, associacao, periodo_vigente)
        ata_paa_factory.create(paa=paa, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
        paa.set_paa_status_gerado()

        _valida(associacao, periodo_proxima_vigencia)

    def test_recusada_com_a_flag_desligada(
            self, paa_factory, documento_paa_factory, associacao, periodo_vigente, periodo_proxima_vigencia):
        _paa_com_plano_gerado(paa_factory, documento_paa_factory, associacao, periodo_vigente)

        with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='não está disponível'):
            _valida(associacao, periodo_proxima_vigencia, habilitada=False)

    def test_paa_vigente_de_outra_associacao_nao_conta_para_a_exigencia(
            self, monkeypatch, paa_factory, documento_paa_factory, associacao, associacao_factory,
            periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('GERADO_PARCIALMENTE',))
        _paa_com_plano_gerado(paa_factory, documento_paa_factory, associacao_factory.create(), periodo_vigente)

        with pytest.raises(PeriodoInvalidoParaElaboracaoException):
            _valida(associacao, periodo_proxima_vigencia)


def test_flag_de_proxima_vigencia_sem_request_consulta_o_banco(flag_paa_proxima_vigencia):
    from sme_ptrf_apps.paa.services.elaboracao_paa_service import proxima_vigencia_habilitada

    assert proxima_vigencia_habilitada() is True
