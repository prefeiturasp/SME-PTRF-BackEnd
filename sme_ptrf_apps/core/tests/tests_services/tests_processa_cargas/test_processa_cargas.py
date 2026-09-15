from unittest.mock import patch

import pytest
from waffle.testutils import override_flag

from sme_ptrf_apps.core.choices.tipos_carga import (
    CARGA_ACOES_ASSOCIACOES,
    CARGA_ASSOCIACOES,
    CARGA_CENSO,
    CARGA_CONTAS_ASSOCIACOES,
    CARGA_DEVOLUCAO_TESOURO,
    CARGA_MATERIAIS_SERVICOS,
    CARGA_PERIODO_INICIAL,
    CARGA_REPASSE_PREVISTO,
    CARGA_REPASSE_PREVISTO_SME,
    CARGA_REPASSE_REALIZADO,
    CARGA_USUARIOS,
)
from sme_ptrf_apps.core.models.arquivo import PROCESSANDO
from sme_ptrf_apps.core.services.processa_cargas import processa_carga, processa_cargas

pytestmark = pytest.mark.django_db

MODULE = 'sme_ptrf_apps.core.services.processa_cargas'


def test_processa_carga_inicia_processamento(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_REPASSE_REALIZADO)

    with patch(f'{MODULE}.carrega_repasses_realizados'):
        processa_carga(arquivo)

    arquivo.refresh_from_db()
    assert arquivo.status == PROCESSANDO


def test_processa_carga_repasse_realizado(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_REPASSE_REALIZADO)

    with patch(f'{MODULE}.carrega_repasses_realizados') as mock_func:
        processa_carga(arquivo)

    mock_func.assert_called_once_with(arquivo)


def test_processa_carga_periodo_inicial(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_PERIODO_INICIAL)

    with patch(f'{MODULE}.carrega_periodo_inicial') as mock_func:
        processa_carga(arquivo)

    mock_func.assert_called_once_with(arquivo)


def test_processa_carga_repasse_previsto(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_REPASSE_PREVISTO)

    with patch(f'{MODULE}.carrega_repasses_previstos') as mock_func:
        processa_carga(arquivo)

    mock_func.assert_called_once_with(arquivo)


def test_processa_carga_associacoes(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_ASSOCIACOES)

    with patch(f'{MODULE}.CargaAssociacoesService') as mock_service:
        processa_carga(arquivo)

    mock_service.return_value.carrega_associacoes.assert_called_once_with(arquivo)


def test_processa_carga_contas_associacoes(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_CONTAS_ASSOCIACOES)

    with patch(f'{MODULE}.CargaContasAssociacoesService') as mock_service:
        processa_carga(arquivo)

    mock_service.return_value.carrega_contas_associacoes.assert_called_once_with(arquivo)


def test_processa_carga_acoes_associacoes(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_ACOES_ASSOCIACOES)

    with patch(f'{MODULE}.CargaAcoesAssociacoesService') as mock_service:
        processa_carga(arquivo)

    mock_service.return_value.carrega_acoes_associacoes.assert_called_once_with(arquivo)


def test_processa_carga_usuarios_flag_gestao_usuarios_ativa(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_USUARIOS)

    with override_flag('gestao-usuarios', active=True), \
            patch(f'{MODULE}.CargaUsuariosGestaoUsuarioService') as mock_service_v2, \
            patch(f'{MODULE}.CargaUsuariosService') as mock_service_v1:
        processa_carga(arquivo)

    mock_service_v2.return_value.carrega_usuarios.assert_called_once_with(arquivo)
    mock_service_v1.return_value.carrega_usuarios.assert_not_called()


def test_processa_carga_usuarios_flag_gestao_usuarios_inativa(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_USUARIOS)

    with override_flag('gestao-usuarios', active=False), \
            patch(f'{MODULE}.CargaUsuariosGestaoUsuarioService') as mock_service_v2, \
            patch(f'{MODULE}.CargaUsuariosService') as mock_service_v1:
        processa_carga(arquivo)

    mock_service_v1.return_value.carrega_usuarios.assert_called_once_with(arquivo)
    mock_service_v2.return_value.carrega_usuarios.assert_not_called()


def test_processa_carga_censo(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_CENSO)

    with patch(f'{MODULE}.carrega_censo') as mock_func:
        processa_carga(arquivo)

    mock_func.assert_called_once_with(arquivo)


def test_processa_carga_repasse_previsto_sme(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_REPASSE_PREVISTO_SME)

    with patch(f'{MODULE}.carrega_previsoes_repasses') as mock_func:
        processa_carga(arquivo)

    mock_func.assert_called_once_with(arquivo)


def test_processa_carga_devolucao_tesouro(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_DEVOLUCAO_TESOURO)

    with patch(f'{MODULE}.CargaDevolucoesTesouroService') as mock_service:
        processa_carga(arquivo)

    mock_service.return_value.carrega_devolucoes_tesouro.assert_called_once_with(arquivo)


def test_processa_carga_materiais_servicos(arquivo_factory):
    arquivo = arquivo_factory(tipo_carga=CARGA_MATERIAIS_SERVICOS)

    with patch(f'{MODULE}.CargaMateriaisServicosService') as mock_service:
        processa_carga(arquivo)

    mock_service.return_value.carrega_materiais_servicos.assert_called_once_with(arquivo)


def test_processa_cargas_processa_todos_os_arquivos_do_queryset(arquivo_factory):
    arquivo_1 = arquivo_factory(tipo_carga=CARGA_CENSO, identificador='arquivo-1')
    arquivo_2 = arquivo_factory(tipo_carga=CARGA_REPASSE_PREVISTO_SME, identificador='arquivo-2')

    from sme_ptrf_apps.core.models import Arquivo

    with patch(f'{MODULE}.processa_carga') as mock_processa_carga:
        processa_cargas(Arquivo.objects.filter(uuid__in=[arquivo_1.uuid, arquivo_2.uuid]))

    assert mock_processa_carga.call_count == 2
    mock_processa_carga.assert_any_call(arquivo_1)
    mock_processa_carga.assert_any_call(arquivo_2)
