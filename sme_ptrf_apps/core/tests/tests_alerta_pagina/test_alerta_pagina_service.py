from datetime import date
from unittest.mock import patch

import pytest

from sme_ptrf_apps.core.fixtures.factories import AlertaPaginaFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_inicial_associacao_factory import PeriodoInicialAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import UnidadeFactory, DreFactory
from sme_ptrf_apps.core.services.alerta_pagina_service import AlertaPaginaService
from sme_ptrf_apps.core.choices.alerta_pagina_categoria import AlertaPaginaCategoriaChoices

pytestmark = pytest.mark.django_db

CATEGORIA = AlertaPaginaCategoriaChoices.AVISO_REMOCAO_PRESIDENTE


@pytest.mark.parametrize(
    'data_disparo, hoje, esperado',
    [
        (date(2026, 11, 15), date(2026, 11, 14), None),
        (date(2026, 11, 15), date(2026, 11, 15), date(2026, 11, 15)),
        (date(2026, 11, 15), date(2027, 1, 5), date(2026, 11, 15)),
        (date(2026, 11, 15), date(2026, 1, 1), None),
        (date(2027, 11, 15), date(2026, 12, 1), None),
        (date(2024, 2, 29), date(2025, 3, 5), date(2025, 3, 1)),
    ],
)
def test_ocorrencia_mais_recente(data_disparo, hoje, esperado):
    assert AlertaPaginaService.ocorrencia_mais_recente(data_disparo, hoje) == esperado


@pytest.fixture
def tres_alertas(recurso_legado):
    return [
        AlertaPaginaFactory(recurso=recurso_legado, data_disparo=date(2026, dia_mes[0], dia_mes[1]))
        for dia_mes in ((11, 15), (11, 30), (12, 10))
    ]


@pytest.mark.parametrize(
    'hoje, ocorrencia_esperada',
    [
        (date(2026, 11, 14), None),
        (date(2026, 11, 24), date(2026, 11, 15)),
        (date(2026, 12, 5), date(2026, 11, 30)),
        (date(2026, 12, 15), date(2026, 12, 10)),
        (date(2027, 1, 15), None),
    ],
)
def test_alerta_vigente_escolhe_mais_recente_nao_futuro(tres_alertas, recurso_legado, hoje, ocorrencia_esperada):
    resultado = AlertaPaginaService.alerta_vigente(recurso_legado, CATEGORIA, hoje)

    if ocorrencia_esperada is None:
        assert resultado is None
    else:
        assert resultado[1] == ocorrencia_esperada


def test_alerta_vigente_respeita_limite_da_janela(recurso_legado):
    AlertaPaginaFactory(recurso=recurso_legado, data_disparo=date(2026, 11, 15))

    dentro = AlertaPaginaService.alerta_vigente(recurso_legado, CATEGORIA, date(2026, 11, 24))  # 10 dias
    fora = AlertaPaginaService.alerta_vigente(recurso_legado, CATEGORIA, date(2026, 12, 15))

    assert dentro is not None
    assert fora is None


def test_alerta_vigente_ignora_inativo_e_outro_recurso(recurso_legado):
    AlertaPaginaFactory(recurso=recurso_legado, ativo=False)
    AlertaPaginaFactory(recurso=RecursoFactory())

    assert AlertaPaginaService.alerta_vigente(recurso_legado, CATEGORIA, date(2026, 11, 20)) is None


@pytest.fixture
def unidade_ue_com_recurso(recurso_legado):
    unidade = UnidadeFactory(tipo_unidade='EMEF')
    PeriodoInicialAssociacaoFactory(associacao=AssociacaoFactory(unidade=unidade), recurso=recurso_legado)
    return unidade


def test_alerta_para_unidade_ue_retorna_dados_com_chave(unidade_ue_com_recurso, recurso_legado):
    alerta = AlertaPaginaFactory(recurso=recurso_legado, data_disparo=date(2026, 11, 15))

    resultado = AlertaPaginaService.alerta_para_unidade(
        unidade_ue_com_recurso, recurso_legado, CATEGORIA, date(2026, 11, 20))

    assert resultado['uuid'] == alerta.uuid
    assert resultado['chave'] == f'{alerta.uuid}:2026-11-15'


def test_alerta_para_unidade_dre_retorna_none(recurso_legado):
    AlertaPaginaFactory(recurso=recurso_legado)
    dre = DreFactory()

    assert AlertaPaginaService.alerta_para_unidade(dre, recurso_legado, CATEGORIA, date(2026, 11, 20)) is None


def test_alerta_para_unidade_ue_sem_o_recurso_retorna_none(recurso_legado):
    AlertaPaginaFactory(recurso=recurso_legado)
    unidade = UnidadeFactory(tipo_unidade='EMEF')

    assert AlertaPaginaService.alerta_para_unidade(unidade, recurso_legado, CATEGORIA, date(2026, 11, 20)) is None


def test_data_de_hoje_retorna_data_local_sem_levantar_erro():
    assert AlertaPaginaService.data_de_hoje() == date.today()


def test_alerta_vigente_sem_data_usa_data_de_hoje(recurso_legado):
    AlertaPaginaFactory(recurso=recurso_legado, data_disparo=date(2026, 11, 15))

    with patch.object(AlertaPaginaService, 'data_de_hoje', return_value=date(2026, 11, 20)):
        resultado = AlertaPaginaService.alerta_vigente(recurso_legado, CATEGORIA)

    assert resultado[1] == date(2026, 11, 15)


def test_alerta_para_unidade_sem_data_usa_data_de_hoje(unidade_ue_com_recurso, recurso_legado):
    alerta = AlertaPaginaFactory(recurso=recurso_legado, data_disparo=date(2026, 11, 15))

    with patch.object(AlertaPaginaService, 'data_de_hoje', return_value=date(2026, 11, 20)):
        resultado = AlertaPaginaService.alerta_para_unidade(unidade_ue_com_recurso, recurso_legado, CATEGORIA)

    assert resultado['uuid'] == alerta.uuid
