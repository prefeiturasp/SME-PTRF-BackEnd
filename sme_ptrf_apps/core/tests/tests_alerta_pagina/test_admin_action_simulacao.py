from datetime import date
from unittest.mock import patch

import pytest
from django.contrib import admin
from django.test import Client, RequestFactory
from django.urls import reverse

from sme_ptrf_apps.core.admin import AlertaPaginaAdmin
from sme_ptrf_apps.core.models import AlertaPagina
from sme_ptrf_apps.core.services.alerta_pagina_service import AlertaPaginaService
from sme_ptrf_apps.users.fixtures.factories import UsuarioFactory

pytestmark = pytest.mark.django_db

SERVICO = 'sme_ptrf_apps.core.services.alerta_pagina_email_service'
URL = 'admin:core_alertapagina_changelist'


@pytest.fixture
def cliente_admin():
    superusuario = UsuarioFactory(is_staff=True, is_superuser=True)
    cliente = Client()
    cliente.force_login(superusuario)
    return cliente


def _postar(cliente, alerta, **extra):
    dados = {'action': 'simular_envio_email', '_selected_action': [alerta.pk], 'index': 0, **extra}
    return cliente.post(reverse(URL), dados)


def test_action_exibe_simulacao_com_data_de_hoje_por_padrao(cliente_admin, alerta):
    with patch.object(AlertaPaginaService, 'data_de_hoje', return_value=date(2026, 11, 15)):
        resposta = _postar(cliente_admin, alerta)

    assert resposta.status_code == 200
    [resultado] = resposta.context['resultados']
    assert resultado['dispara'] is True
    assert 'Nenhum e-mail é enviado' in resposta.content.decode()


def test_action_simula_data_informada_com_detalhes(cliente_admin, alerta, criar_usuario, grupo, unidade_ue):
    criar_usuario(grupo, [unidade_ue], username='123456')
    alerta.texto = '<p>Texto do aviso</p>'
    alerta.save()

    resposta = _postar(cliente_admin, alerta, simular=1, data='2026-11-15')

    [resultado] = resposta.context['resultados']
    conteudo = resposta.content.decode()
    assert resultado['dispara'] is True
    assert resultado['total_destinatarios'] == 1
    assert 'DISPARA' in conteudo and '123456' in conteudo and 'Texto do aviso' in conteudo


def test_action_data_invalida_nao_simula(cliente_admin, alerta):
    resposta = _postar(cliente_admin, alerta, simular=1, data='invalida')

    assert resposta.status_code == 200
    assert resposta.context['resultados'] == []
    assert resposta.context['form'].errors


def test_action_nao_envia_nem_grava(cliente_admin, alerta, criar_usuario, grupo, unidade_ue):
    criar_usuario(grupo, [unidade_ue])

    with patch(f'{SERVICO}.enviar_email_nova_notificacao_v2') as mock_envio:
        _postar(cliente_admin, alerta, simular=1, data='2026-11-15')

    mock_envio.assert_not_called()
    alerta.refresh_from_db()
    assert alerta.ultimo_envio_email_em is None


def test_action_alerta_inativo_informa_motivo(cliente_admin, alerta):
    alerta.ativo = False
    alerta.save()

    resposta = _postar(cliente_admin, alerta, simular=1, data='2026-11-15')

    [resultado] = resposta.context['resultados']
    assert resultado['dispara'] is False


def test_permissao_exige_change_alertapagina():
    modelo_admin = AlertaPaginaAdmin(AlertaPagina, admin.site)
    fabrica = RequestFactory()

    request_superusuario = fabrica.get('/')
    request_superusuario.user = UsuarioFactory(is_staff=True, is_superuser=True)
    request_sem_permissao = fabrica.get('/')
    request_sem_permissao.user = UsuarioFactory(is_staff=True)

    assert modelo_admin.has_simular_envio_permission(request_superusuario) is True
    assert modelo_admin.has_simular_envio_permission(request_sem_permissao) is False
