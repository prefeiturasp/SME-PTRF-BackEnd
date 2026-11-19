from datetime import date

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from freezegun import freeze_time

from sme_ptrf_apps.paa.enums import PaaStatusAndamentoEnum, PaaStatusEnum
from sme_ptrf_apps.paa.models import DocumentoPaa
from sme_ptrf_apps.paa.services import VigenciaElaboracaoPaaService

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


@pytest.fixture
def parametro_outubro(parametro_paa_factory):
    return parametro_paa_factory.create(mes_elaboracao_paa=10)


def test_retorna_fatos_e_classifica_a_vigencia(
        associacao, periodo_vigente, periodo_proxima_vigencia, parametro_outubro):
    vigencia = VigenciaElaboracaoPaaService.obter(associacao, proxima_vigencia_habilitada=True, hoje=HOJE)

    assert vigencia['hoje'] == HOJE
    assert vigencia['mes_elaboracao_paa'] == 10
    assert vigencia['proxima_vigencia_habilitada'] is True
    assert vigencia['periodos_sobrepostos'] is False
    assert [(p['referencia'], p['vigencia'], p['paa']) for p in vigencia['periodos']] == [
        ('2026', 'VIGENTE', None),
        ('2027', 'PROXIMA_VIGENCIA', None),
    ]


def test_resume_paa_em_elaboracao_e_gerado_parcialmente(
        paa_factory, documento_paa_factory, periodo_vigente, periodo_proxima_vigencia, parametro_outubro):
    paa_vigente = paa_factory.create(periodo_paa=periodo_vigente)
    documento_paa_factory.create(
        paa=paa_vigente, versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)
    paa_proximo = paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=paa_vigente.associacao)

    vigencia = VigenciaElaboracaoPaaService.obter(paa_vigente.associacao, True, hoje=HOJE)

    vigente, proxima = vigencia['periodos']
    assert vigente['paa'] == {
        'uuid': paa_vigente.uuid,
        'status': PaaStatusEnum.EM_ELABORACAO.name,
        'status_andamento': PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
    }
    assert proxima['paa']['uuid'] == paa_proximo.uuid
    assert proxima['paa']['status_andamento'] == PaaStatusAndamentoEnum.EM_ELABORACAO.name


def test_paa_de_outra_associacao_nao_aparece(
        paa_factory, associacao, periodo_vigente, parametro_outubro):
    paa_factory.create(periodo_paa=periodo_vigente)

    vigencia = VigenciaElaboracaoPaaService.obter(associacao, True, hoje=HOJE)

    assert vigencia['periodos'][0]['paa'] is None


@freeze_time('2026-10-28')
def test_hoje_padrao_e_a_data_atual(associacao, parametro_outubro):
    vigencia = VigenciaElaboracaoPaaService.obter(associacao, False)

    assert vigencia['hoje'] == HOJE
    assert vigencia['proxima_vigencia_habilitada'] is False


def test_numero_de_queries_nao_cresce_com_o_numero_de_periodos(
        associacao, periodo_paa_factory, parametro_outubro):
    def cria_periodos(ano_inicial, quantidade):
        for ano in range(ano_inicial, ano_inicial + quantidade):
            periodo_paa_factory.create(
                referencia=str(ano), data_inicial=date(ano, 1, 1), data_final=date(ano, 12, 31))

    cria_periodos(2026, 2)
    VigenciaElaboracaoPaaService.obter(associacao, True, hoje=HOJE)
    with CaptureQueriesContext(connection) as poucos:
        VigenciaElaboracaoPaaService.obter(associacao, True, hoje=HOJE)

    cria_periodos(2028, 5)
    with CaptureQueriesContext(connection) as muitos:
        VigenciaElaboracaoPaaService.obter(associacao, True, hoje=HOJE)

    assert len(muitos) == len(poucos)


def test_informa_a_exigencia_sobre_o_paa_vigente(monkeypatch, associacao, parametro_paa_factory):
    from sme_ptrf_apps.paa import constantes
    parametro_paa_factory.create(mes_elaboracao_paa=10)

    sem_exigencia = VigenciaElaboracaoPaaService.obter(associacao, True, hoje=date(2026, 10, 28))
    monkeypatch.setattr(
        constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('GERADO',))
    com_exigencia = VigenciaElaboracaoPaaService.obter(associacao, True, hoje=date(2026, 10, 28))

    assert sem_exigencia['status_vigente_exigidos_para_proxima_vigencia'] is None
    assert com_exigencia['status_vigente_exigidos_para_proxima_vigencia'] == ('GERADO',)
