"""O PAA só gera documentos (e, se parametrizado, só é retificado) com o PAA do período anterior concluído."""
from datetime import date

import pytest
from rest_framework import status

from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa
from sme_ptrf_apps.paa.services.ata_paa_service import validar_geracao_ata_paa
from sme_ptrf_apps.paa.services.paa_anterior_service import PaaAnteriorService
from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService, ValidacaoRetificacao
from sme_ptrf_apps.paa.services.valida_geracao_documentos_service import (
    ValidaGeracaoDocumentoException, ValidaGeracaoDocumentoPAAService)

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_paa_anterior(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))


@pytest.fixture
def periodo_paa_seguinte(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 5, 1), data_final=date(2027, 12, 31))


@pytest.fixture
def paa_anterior(paa_factory, associacao, periodo_paa_anterior):
    return paa_factory.create(periodo_paa=periodo_paa_anterior, associacao=associacao)


@pytest.fixture
def paa_seguinte(paa_factory, associacao, periodo_paa_seguinte):
    return paa_factory.create(periodo_paa=periodo_paa_seguinte, associacao=associacao)


def _gera_plano(documento_paa_factory, paa):
    documento_paa_factory.create(
        paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)


def _gera_ata(ata_paa_factory, paa):
    ata_paa_factory.create(paa=paa, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
    paa.set_paa_status_gerado()


def _gerado(documento_paa_factory, ata_paa_factory, paa):
    _gera_plano(documento_paa_factory, paa)
    _gera_ata(ata_paa_factory, paa)


class TestPaaAnteriorService:

    def test_sem_periodo_anterior_nao_ha_paa_anterior(self, paa_anterior):
        assert PaaAnteriorService.paa_do_periodo_anterior(paa_anterior) is None

    def test_periodo_anterior_sem_paa_da_associacao(self, periodo_paa_anterior, paa_seguinte):
        assert PaaAnteriorService.paa_do_periodo_anterior(paa_seguinte) is None

    def test_paa_de_outra_associacao_nao_conta(
            self, paa_factory, associacao_factory, periodo_paa_anterior, paa_seguinte):
        paa_factory.create(periodo_paa=periodo_paa_anterior, associacao=associacao_factory.create())

        assert PaaAnteriorService.paa_do_periodo_anterior(paa_seguinte) is None

    def test_paa_do_periodo_imediatamente_anterior(self, paa_anterior, paa_seguinte):
        assert PaaAnteriorService.paa_do_periodo_anterior(paa_seguinte) == paa_anterior

    def test_exigencia_none_sempre_atende(self, paa_anterior, paa_seguinte):
        assert PaaAnteriorService.atende_exigencia(paa_seguinte, None) is True

    def test_sem_paa_anterior_atende(self, periodo_paa_anterior, paa_seguinte):
        assert PaaAnteriorService.atende_exigencia(paa_seguinte, ('GERADO',)) is True


class TestBloqueioDeGeracao:

    def test_sem_paa_anterior_libera(self, paa_seguinte):
        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa_seguinte)

    def test_anterior_em_elaboracao_bloqueia_previa_e_final(self, paa_anterior, paa_seguinte):
        for validar in (ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa,
                        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final):
            with pytest.raises(ValidaGeracaoDocumentoException, match='ainda não foi concluído'):
                validar(paa_seguinte)

    def test_anterior_com_ata_pendente_bloqueia_com_a_mensagem_da_historia(
            self, documento_paa_factory, paa_anterior, paa_seguinte):
        _gera_plano(documento_paa_factory, paa_anterior)

        with pytest.raises(ValidaGeracaoDocumentoException, match='ata de apresentação do PAA anterior'):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa_seguinte)

    def test_anterior_em_retificacao_bloqueia(
            self, documento_paa_factory, ata_paa_factory, paa_anterior, paa_seguinte):
        _gerado(documento_paa_factory, ata_paa_factory, paa_anterior)
        paa_anterior.set_paa_status_em_retificacao()

        with pytest.raises(ValidaGeracaoDocumentoException, match='retificação em andamento'):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa_seguinte)

    def test_anterior_gerado_libera(self, documento_paa_factory, ata_paa_factory, paa_anterior, paa_seguinte):
        _gerado(documento_paa_factory, ata_paa_factory, paa_anterior)

        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa_seguinte)

    def test_mensagem_do_proprio_paa_tem_prioridade(self, documento_paa_factory, paa_anterior, paa_seguinte):
        _gera_plano(documento_paa_factory, paa_seguinte)

        with pytest.raises(ValidaGeracaoDocumentoException, match='Já existe uma versão final gerada'):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa_seguinte)

    def test_sem_exigencia_parametrizada_libera(self, monkeypatch, paa_anterior, paa_seguinte):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ANTERIOR_EXIGIDOS_PARA_GERAR_DOCUMENTOS', None)

        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa_seguinte)

    def test_exigencia_parametrizada_aceita_ata_pendente(
            self, monkeypatch, documento_paa_factory, paa_anterior, paa_seguinte):
        monkeypatch.setattr(
            constantes, 'STATUS_PAA_ANTERIOR_EXIGIDOS_PARA_GERAR_DOCUMENTOS', ('GERADO_PARCIALMENTE', 'GERADO'))
        _gera_plano(documento_paa_factory, paa_anterior)

        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa_seguinte)

    def test_endpoint_de_geracao_final_responde_400_com_o_erro_conhecido_pelo_frontend(
            self, jwt_authenticated_client_sme, flag_paa, paa_anterior, paa_seguinte):
        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa_seguinte.uuid}/gerar-documento/', content_type='application/json', data='{}')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['error'] == 'valida_gerar_documento_final'
        assert 'PAA anterior' in response.json()['mensagem']


class TestBloqueioDaAta:

    def test_ata_de_apresentacao_do_seguinte_com_anterior_pendente(
            self, documento_paa_factory, ata_paa_factory, paa_anterior, paa_seguinte):
        _gera_plano(documento_paa_factory, paa_seguinte)
        ata = ata_paa_factory.create(paa=paa_seguinte, tipo_ata='APRESENTACAO')

        resultado = validar_geracao_ata_paa(ata)

        assert resultado['is_valid'] is False
        assert 'PAA anterior' in resultado['mensagem']


class TestExigenciaParaRetificar:

    @pytest.fixture
    def flag_retificacao(self, flag_factory):
        return flag_factory.create(name='paa-retificacao', everyone=True)

    @pytest.fixture
    def seguinte_gerado(self, documento_paa_factory, ata_paa_factory, paa_seguinte):
        _gerado(documento_paa_factory, ata_paa_factory, paa_seguinte)
        return paa_seguinte

    def test_por_padrao_retifica_com_o_anterior_em_qualquer_situacao(
            self, flag_retificacao, paa_anterior, seguinte_gerado):
        RetificacaoPaaService(seguinte_gerado, usuario='u').valida_pode_retificar()

    def test_exigencia_parametrizada_recusa_anterior_nao_gerado(
            self, monkeypatch, flag_retificacao, paa_anterior, seguinte_gerado):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ANTERIOR_EXIGIDOS_PARA_RETIFICAR', ('GERADO',))

        with pytest.raises(ValidacaoRetificacao, match='PAA anterior'):
            RetificacaoPaaService(seguinte_gerado, usuario='u').valida_pode_retificar()

    def test_exigencia_parametrizada_aceita_anterior_gerado(
            self, monkeypatch, flag_retificacao, documento_paa_factory, ata_paa_factory, paa_anterior,
            seguinte_gerado):

        monkeypatch.setattr(constantes, 'STATUS_PAA_ANTERIOR_EXIGIDOS_PARA_RETIFICAR', ('GERADO',))
        _gerado(documento_paa_factory, ata_paa_factory, paa_anterior)

        RetificacaoPaaService(seguinte_gerado, usuario='u').valida_pode_retificar()
