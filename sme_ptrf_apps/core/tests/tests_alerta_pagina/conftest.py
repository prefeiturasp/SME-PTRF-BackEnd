from datetime import date

import pytest

from sme_ptrf_apps.core.fixtures.factories import (
    AlertaPaginaFactory,
    AssociacaoFactory,
    PeriodoInicialAssociacaoFactory,
    UnidadeFactory,
)
from sme_ptrf_apps.users.fixtures.factories import GrupoAcessoFactory, UsuarioFactory


@pytest.fixture(autouse=True)
def server_name(monkeypatch):
    monkeypatch.setenv('SERVER_NAME', 'sigescola.exemplo.gov.br')


@pytest.fixture
def grupo():
    return GrupoAcessoFactory()


@pytest.fixture
def unidade_ue(recurso_legado):
    unidade = UnidadeFactory(tipo_unidade='EMEF')
    PeriodoInicialAssociacaoFactory(associacao=AssociacaoFactory(unidade=unidade), recurso=recurso_legado)
    return unidade


@pytest.fixture
def alerta(recurso_legado, grupo):
    return AlertaPaginaFactory(
        recurso=recurso_legado, enviar_email=True, assunto_email='Aviso', grupos_email=[grupo],
        data_disparo=date(2026, 11, 15))


@pytest.fixture
def criar_usuario():
    def _criar(grupo, unidades, **kwargs):
        usuario = UsuarioFactory(unidades=unidades, **kwargs)
        usuario.groups.add(grupo)
        return usuario
    return _criar
