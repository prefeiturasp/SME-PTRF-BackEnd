from datetime import date
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from rest_framework import status

from sme_ptrf_apps.paa.api.serializers.paa_serializer import PaaSerializer
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa, PeriodoPaa, PrioridadePaa, ReceitaPrevistaPdde
from sme_ptrf_apps.paa.services import AcoesPddeService

pytestmark = pytest.mark.django_db

HOJE = '2026-10-28'


@pytest.fixture
def periodo_vigente(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))


@pytest.fixture
def periodo_proxima_vigencia(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 8, 1), data_final=date(2027, 12, 31))


@pytest.fixture
def paa_vigente(paa_factory, associacao, periodo_vigente):
    return paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao, texto_introducao='vigente')


@pytest.fixture
def paa_proxima_vigencia(paa_factory, associacao, periodo_proxima_vigencia):
    return paa_factory.create(
        periodo_paa=periodo_proxima_vigencia, associacao=associacao, texto_introducao='proxima')


def _gera_plano(documento_paa_factory, paa):
    documento_paa_factory.create(
        paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)


def _gera_ata(ata_paa_factory, paa):
    ata_paa_factory.create(paa=paa, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
    paa.set_paa_status_gerado()


class TestIndependencia:

    def test_dados_de_um_paa_nao_aparecem_no_outro(
            self, prioridade_paa_factory, receita_prevista_pdde_factory, paa_vigente, paa_proxima_vigencia):
        prioridade_paa_factory.create(paa=paa_proxima_vigencia)
        receita_prevista_pdde_factory.create(paa=paa_proxima_vigencia)

        assert PrioridadePaa.objects.filter(paa=paa_vigente).count() == 0
        assert ReceitaPrevistaPdde.objects.filter(paa=paa_vigente).count() == 0
        assert PrioridadePaa.objects.filter(paa=paa_proxima_vigencia).count() == 1

    def test_editar_o_paa_da_proxima_vigencia_nao_altera_o_vigente(
            self, documento_paa_factory, paa_vigente, paa_proxima_vigencia):
        _gera_plano(documento_paa_factory, paa_vigente)
        antes = (paa_vigente.status, paa_vigente.get_status_andamento(), paa_vigente.texto_introducao)

        paa_proxima_vigencia.texto_introducao = 'alterado'
        paa_proxima_vigencia.save()

        paa_vigente.refresh_from_db()
        assert (paa_vigente.status, paa_vigente.get_status_andamento(), paa_vigente.texto_introducao) == antes

    def test_cada_paa_tem_status_e_andamento_proprios(
            self, documento_paa_factory, ata_paa_factory, paa_vigente, paa_proxima_vigencia):
        _gera_plano(documento_paa_factory, paa_vigente)
        _gera_ata(ata_paa_factory, paa_vigente)

        paa_vigente.refresh_from_db()
        paa_proxima_vigencia.refresh_from_db()

        assert paa_vigente.get_status_andamento() == 'GERADO'
        assert paa_proxima_vigencia.get_status_andamento() == 'EM_ELABORACAO'
        assert paa_proxima_vigencia.status_em_elaboracao

    def test_um_paa_por_periodo_e_associacao(self, paa_factory, paa_vigente):
        from django.db import IntegrityError, transaction

        with pytest.raises(IntegrityError), transaction.atomic():
            paa_factory.create(periodo_paa=paa_vigente.periodo_paa, associacao=paa_vigente.associacao)


class TestVigenciaNoSerializer:

    @freeze_time(HOJE)
    def test_classifica_cada_paa(self, flag_paa_proxima_vigencia, paa_vigente, paa_proxima_vigencia):
        assert PaaSerializer(paa_vigente).data['vigencia'] == 'VIGENTE'
        assert PaaSerializer(paa_proxima_vigencia).data['vigencia'] == 'PROXIMA_VIGENCIA'

    @freeze_time(HOJE)
    def test_sem_a_flag_a_vigencia_e_nula(self, paa_vigente, paa_proxima_vigencia):
        assert PaaSerializer(paa_vigente).data['vigencia'] is None
        assert PaaSerializer(paa_proxima_vigencia).data['vigencia'] is None

    @freeze_time(HOJE)
    def test_listagem_calcula_a_vigencia_uma_unica_vez(
            self, flag_paa_proxima_vigencia, paa_factory, associacao_factory,
            periodo_vigente, periodo_proxima_vigencia):
        paas = [
            paa_factory.create(periodo_paa=periodo, associacao=associacao_factory.create())
            for periodo in (periodo_vigente, periodo_proxima_vigencia) for _ in range(3)
        ]

        with patch.object(
                PeriodoPaa, 'vigente_e_proxima_vigencia_em',
                wraps=PeriodoPaa.vigente_e_proxima_vigencia_em) as espiao:
            dados = PaaSerializer(many=True, instance=paas).data

        assert espiao.call_count == 1
        assert [item['vigencia'] for item in dados] == ['VIGENTE'] * 3 + ['PROXIMA_VIGENCIA'] * 3


class TestListagemVigenteEAnteriores:

    @freeze_time(HOJE)
    def test_inclui_a_proxima_vigencia_com_plano_gerado(
            self, jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, documento_paa_factory, associacao,
            paa_vigente, paa_proxima_vigencia):
        _gera_plano(documento_paa_factory, paa_vigente)
        _gera_plano(documento_paa_factory, paa_proxima_vigencia)

        response = jwt_authenticated_client_sme.get(
            '/api/paa/paa-vigente-e-anteriores/', {'associacao_uuid': associacao.uuid})

        corpo = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert corpo['vigente']['uuid'] == str(paa_vigente.uuid)
        assert corpo['proxima_vigencia']['uuid'] == str(paa_proxima_vigencia.uuid)
        assert corpo['anteriores'] == []

    @freeze_time(HOJE)
    def test_proxima_vigencia_em_elaboracao_nao_aparece_na_listagem(
            self, jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, documento_paa_factory, associacao,
            paa_vigente, paa_proxima_vigencia):
        _gera_plano(documento_paa_factory, paa_vigente)

        corpo = jwt_authenticated_client_sme.get(
            '/api/paa/paa-vigente-e-anteriores/', {'associacao_uuid': associacao.uuid}).json()

        assert corpo['proxima_vigencia'] is None

    @freeze_time(HOJE)
    def test_sem_a_flag_nao_expoe_a_proxima_vigencia(
            self, jwt_authenticated_client_sme, flag_paa, documento_paa_factory, associacao,
            paa_vigente, paa_proxima_vigencia):
        _gera_plano(documento_paa_factory, paa_vigente)
        _gera_plano(documento_paa_factory, paa_proxima_vigencia)

        corpo = jwt_authenticated_client_sme.get(
            '/api/paa/paa-vigente-e-anteriores/', {'associacao_uuid': associacao.uuid}).json()

        assert corpo['vigente']['uuid'] == str(paa_vigente.uuid)
        assert 'proxima_vigencia' not in corpo


class TestAcoesPddeFiltroDePeriodo:

    def test_com_a_flag_ligada_considera_paas_de_varios_periodos(
            self, acao_pdde_factory, receita_prevista_pdde_factory, prioridade_paa_factory,
            paa_proxima_vigencia):
        acao = acao_pdde_factory.create()
        receita = receita_prevista_pdde_factory.create(paa=paa_proxima_vigencia, acao_pdde=acao)
        prioridade = prioridade_paa_factory.create(paa=paa_proxima_vigencia, acao_pdde=acao)

        service = AcoesPddeService(acao, flag_proxima_vigencia_habilitada=True)

        assert list(service.acoes_pdde_receitas_previstas_paas_elaboracao()) == [receita]
        assert list(service.acoes_pdde_prioridades_paas_elaboracao()) == [prioridade]

    @freeze_time(HOJE)
    def test_sem_a_flag_considera_somente_o_periodo_vigente(
            self, acao_pdde_factory, receita_prevista_pdde_factory, prioridade_paa_factory,
            paa_vigente, paa_proxima_vigencia):
        acao = acao_pdde_factory.create()
        receita_vigente = receita_prevista_pdde_factory.create(paa=paa_vigente, acao_pdde=acao)
        prioridade_vigente = prioridade_paa_factory.create(paa=paa_vigente, acao_pdde=acao)
        receita_prevista_pdde_factory.create(paa=paa_proxima_vigencia, acao_pdde=acao)
        prioridade_paa_factory.create(paa=paa_proxima_vigencia, acao_pdde=acao)

        service = AcoesPddeService(acao)

        assert list(service.acoes_pdde_receitas_previstas_paas_elaboracao()) == [receita_vigente]
        assert list(service.acoes_pdde_prioridades_paas_elaboracao()) == [prioridade_vigente]
