from datetime import date
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from sme_ptrf_apps.core.fixtures.factories import AlertaPaginaFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_inicial_associacao_factory import PeriodoInicialAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import UnidadeFactory
from sme_ptrf_apps.core.services.alerta_pagina_service import AlertaPaginaService
from sme_ptrf_apps.users.fixtures.factories import UsuarioFactory

pytestmark = pytest.mark.django_db

URL = '/api/alertas-paginas/vigente/'


@pytest.fixture
def cliente_autenticado():
    cliente = APIClient()
    cliente.force_authenticate(user=UsuarioFactory())
    return cliente


@pytest.fixture
def unidade_ue_com_recurso(recurso_legado):
    unidade = UnidadeFactory(tipo_unidade='EMEF')
    PeriodoInicialAssociacaoFactory(associacao=AssociacaoFactory(unidade=unidade), recurso=recurso_legado)
    return unidade


def test_vigente_retorna_alerta(cliente_autenticado, unidade_ue_com_recurso, recurso_legado):
    alerta = AlertaPaginaFactory(recurso=recurso_legado, data_disparo=date(2026, 11, 15))

    with patch.object(AlertaPaginaService, 'data_de_hoje', return_value=date(2026, 11, 20)):
        resposta = cliente_autenticado.get(
            URL, {'recurso': str(recurso_legado.uuid), 'unidade': str(unidade_ue_com_recurso.uuid)})

    assert resposta.status_code == 200
    assert resposta.json()['alerta']['chave'] == f'{alerta.uuid}:2026-11-15'
    assert resposta.json()['alerta']['texto'] == alerta.texto


def test_vigente_sem_alerta_retorna_none(cliente_autenticado, unidade_ue_com_recurso, recurso_legado):
    with patch.object(AlertaPaginaService, 'data_de_hoje', return_value=date(2026, 11, 20)):
        resposta = cliente_autenticado.get(
            URL, {'recurso': str(recurso_legado.uuid), 'unidade': str(unidade_ue_com_recurso.uuid)})

    assert resposta.json() == {'alerta': None}


def test_vigente_parametros_invalidos_retorna_400_com_campos(cliente_autenticado):
    resposta = cliente_autenticado.get(URL, {'recurso': 'x'})

    assert resposta.status_code == 400
    assert set(resposta.json()) == {'recurso', 'unidade'}


def test_vigente_exige_autenticacao(recurso_legado, unidade_ue_com_recurso):
    resposta = APIClient().get(
        URL, {'recurso': str(recurso_legado.uuid), 'unidade': str(unidade_ue_com_recurso.uuid)})

    assert resposta.status_code == 401
