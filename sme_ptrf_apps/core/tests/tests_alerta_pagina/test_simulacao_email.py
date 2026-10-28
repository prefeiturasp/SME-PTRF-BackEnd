from datetime import date
from unittest.mock import patch

import pytest

from sme_ptrf_apps.core.services.alerta_pagina_email_service import (
    AlertaPaginaEmailService,
    MOTIVO_FORA_DA_DATA,
    MOTIVO_INATIVO,
    MOTIVO_JA_DISPARADO,
    MOTIVO_SEM_ENVIO_EMAIL,
)
from sme_ptrf_apps.core.services.alerta_pagina_service import AlertaPaginaService
from sme_ptrf_apps.users.tasks.enviar_email_nova_notificacao import contexto_email_nova_notificacao

pytestmark = pytest.mark.django_db

SERVICO = 'sme_ptrf_apps.core.services.alerta_pagina_email_service'
TASK = 'sme_ptrf_apps.core.tasks.enviar_emails_alertas_paginas'
DATA_DISPARO = date(2026, 11, 15)


def _simular(alerta, hoje=DATA_DISPARO, **kwargs):
    return AlertaPaginaEmailService.simular_disparo_do_alerta(alerta, hoje, **kwargs)


def test_simulacao_de_alerta_que_dispara_na_data(alerta, criar_usuario, grupo, unidade_ue):
    criar_usuario(grupo, [unidade_ue])
    alerta.texto = '<strong>Negrito</strong> do aviso'
    alerta.save()

    resultado = _simular(alerta)

    assert resultado['dispara'] is True
    assert resultado['motivo_nao_disparo'] is None
    assert resultado['ocorrencia'] == DATA_DISPARO
    assert resultado['total_destinatarios'] == 1
    assert resultado['grupos'] == [grupo.name]
    assert resultado['assunto'] == 'Aviso'
    assert 'Negrito do aviso' in resultado['corpo_html']
    assert '<strong>' not in resultado['corpo_html']


def test_simulacao_usa_categoria_como_assunto_quando_vazio(alerta):
    alerta.assunto_email = ''
    alerta.save()

    assert _simular(alerta)['assunto'] == alerta.get_categoria_display()


def test_simulacao_fora_da_data_informa_motivo_e_mantem_contagem(alerta, criar_usuario, grupo, unidade_ue):
    criar_usuario(grupo, [unidade_ue])

    resultado = _simular(alerta, hoje=date(2026, 11, 16))

    assert resultado['dispara'] is False
    assert resultado['motivo_nao_disparo'] == MOTIVO_FORA_DA_DATA
    assert resultado['total_destinatarios'] == 1


def test_simulacao_de_alerta_ja_disparado_informa_motivo(alerta):
    alerta.ultimo_envio_email_em = DATA_DISPARO
    alerta.save()

    assert _simular(alerta)['motivo_nao_disparo'] == MOTIVO_JA_DISPARADO


def test_simulacao_de_alerta_inativo_informa_motivo(alerta):
    alerta.ativo = False
    alerta.save()

    assert _simular(alerta)['motivo_nao_disparo'] == MOTIVO_INATIVO


def test_simulacao_de_alerta_sem_envio_de_email_informa_motivo(alerta):
    alerta.enviar_email = False
    alerta.save()

    assert _simular(alerta)['motivo_nao_disparo'] == MOTIVO_SEM_ENVIO_EMAIL


def test_simulacao_sem_destinatarios(alerta):
    resultado = _simular(alerta)

    assert resultado['total_destinatarios'] == 0
    assert resultado['amostra_logins'] == []


def test_simulacao_limita_e_ordena_a_amostra_de_logins(alerta, criar_usuario, grupo, unidade_ue):
    for login in ('300', '100', '200'):
        criar_usuario(grupo, [unidade_ue], username=login)

    resultado = _simular(alerta, tamanho_amostra=2)

    assert resultado['total_destinatarios'] == 3
    assert resultado['amostra_logins'] == ['100', '200']


def test_simulacao_usa_amostra_padrao_de_cinco_logins(alerta, criar_usuario, grupo, unidade_ue):
    for login in range(1, 8):
        criar_usuario(grupo, [unidade_ue], username=f'10{login}')

    resultado = _simular(alerta)

    assert resultado['total_destinatarios'] == 7
    assert len(resultado['amostra_logins']) == 5


def test_simulacao_nao_envia_nem_grava(alerta, criar_usuario, grupo, unidade_ue):
    criar_usuario(grupo, [unidade_ue])

    with patch(f'{SERVICO}.enviar_email_nova_notificacao_v2') as mock_envio, \
            patch(f'{TASK}.enviar_email_alerta_pagina_usuario_async.delay') as mock_delay:
        _simular(alerta)

    mock_envio.assert_not_called()
    mock_delay.assert_not_called()
    alerta.refresh_from_db()
    assert alerta.ultimo_envio_email_em is None


def test_simulacao_equivale_ao_disparo_real(alerta, criar_usuario, grupo, unidade_ue):
    criar_usuario(grupo, [unidade_ue])
    criar_usuario(grupo, [unidade_ue])

    simulado = _simular(alerta)
    disparos = AlertaPaginaEmailService.registrar_disparos_do_dia(DATA_DISPARO)
    alerta.refresh_from_db()
    depois = _simular(alerta)

    assert simulado['dispara'] is True
    assert simulado['total_destinatarios'] == len(disparos) == 2
    assert depois['dispara'] is False
    assert depois['motivo_nao_disparo'] == MOTIVO_JA_DISPARADO


def test_data_de_hoje_usa_o_fuso_do_projeto_sem_levantar_erro():
    assert AlertaPaginaService.data_de_hoje() == date.today()


def test_registrar_disparos_sem_data_usa_data_de_hoje(alerta):
    with patch.object(AlertaPaginaService, 'data_de_hoje', return_value=DATA_DISPARO):
        disparos = AlertaPaginaEmailService.registrar_disparos_do_dia()

    alerta.refresh_from_db()
    assert disparos == []
    assert alerta.ultimo_envio_email_em == DATA_DISPARO


def test_contexto_do_email_usa_server_name():
    contexto = contexto_email_nova_notificacao(username='123', nome='Maria', descricao='Texto')

    assert contexto['url'] == 'https://sigescola.exemplo.gov.br/'
    assert contexto['server_name'] == 'https://sigescola.exemplo.gov.br'
    assert (contexto['login'], contexto['nome'], contexto['descricao']) == ('123', 'Maria', 'Texto')
