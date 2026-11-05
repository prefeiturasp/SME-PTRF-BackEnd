from datetime import date
from unittest.mock import patch

import pytest

from sme_ptrf_apps.core.fixtures.factories import AlertaPaginaFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_inicial_associacao_factory import PeriodoInicialAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import UnidadeFactory, DreFactory
from sme_ptrf_apps.core.services.alerta_pagina_email_service import AlertaPaginaEmailService
from sme_ptrf_apps.users.fixtures.factories import UsuarioFactory, GrupoAcessoFactory

pytestmark = pytest.mark.django_db

SERVICO = 'sme_ptrf_apps.core.services.alerta_pagina_email_service'


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


def _usuario(grupo, unidades, **kwargs):
    usuario = UsuarioFactory(unidades=unidades, **kwargs)
    usuario.groups.add(grupo)
    return usuario


def test_destinatarios_inclui_apenas_usuarios_elegiveis(alerta, grupo, unidade_ue):
    elegivel = _usuario(grupo, [unidade_ue])
    misto = _usuario(grupo, [unidade_ue, DreFactory()])
    _usuario(grupo, [DreFactory()])
    _usuario(grupo, [unidade_ue], is_active=False)
    UsuarioFactory(unidades=[unidade_ue])

    destinatarios = set(AlertaPaginaEmailService.usuarios_destinatarios(alerta))

    assert destinatarios == {elegivel, misto}


def test_registrar_disparos_do_dia_marca_e_nao_repete(alerta, grupo, unidade_ue):
    usuario = _usuario(grupo, [unidade_ue])

    primeiro = AlertaPaginaEmailService.registrar_disparos_do_dia(date(2026, 11, 15))
    segundo = AlertaPaginaEmailService.registrar_disparos_do_dia(date(2026, 11, 15))

    alerta.refresh_from_db()
    assert primeiro == [(alerta.id, usuario.id, date(2026, 11, 15).isoformat())]
    assert segundo == []
    assert alerta.ultimo_envio_email_em == date(2026, 11, 15)


def test_registrar_disparos_fora_do_dia_ou_sem_email_nao_dispara(alerta, grupo, unidade_ue, recurso_legado):
    _usuario(grupo, [unidade_ue])
    AlertaPaginaFactory(
        recurso=recurso_legado, enviar_email=False, data_disparo=date(2026, 11, 16))

    assert AlertaPaginaEmailService.registrar_disparos_do_dia(date(2026, 11, 16)) == []
    alerta.refresh_from_db()
    assert alerta.ultimo_envio_email_em is None


def test_enviar_para_usuario_usa_assunto_e_texto_sem_html(alerta, grupo, unidade_ue):
    usuario = _usuario(grupo, [unidade_ue])
    alerta.texto = '<p>Presidente&nbsp;em remoção</p>'
    alerta.save()

    with patch(f'{SERVICO}.enviar_email_nova_notificacao_v2') as mock_envio:
        enviado = AlertaPaginaEmailService.enviar_para_usuario(alerta.id, usuario.id)

    assert enviado is True
    mock_envio.assert_called_once_with(
        usuario=usuario, titulo='Aviso', descricao='Presidente\xa0em remoção')


def test_enviar_para_usuario_inexistente_retorna_false_sem_enviar(alerta):
    with patch(f'{SERVICO}.enviar_email_nova_notificacao_v2') as mock_envio:
        assert AlertaPaginaEmailService.enviar_para_usuario(alerta.id, 0) is False
        assert AlertaPaginaEmailService.enviar_para_usuario(0, 1) is False

    mock_envio.assert_not_called()


def test_nao_envia_email_duplicado(
    alerta, grupo, unidade_ue, criar_usuario
):
    usuario = criar_usuario(grupo, [unidade_ue])
    ocorrencia = date(2026, 11, 15)

    with patch(
        f'{SERVICO}.enviar_email_nova_notificacao_v2',
        return_value=True,
    ) as mock_envio:
        primeiro = AlertaPaginaEmailService.enviar_para_usuario(
            alerta.id, usuario.id, ocorrencia
        )
        segundo = AlertaPaginaEmailService.enviar_para_usuario(
            alerta.id, usuario.id, ocorrencia
        )

    assert primeiro is True
    assert segundo is False
    mock_envio.assert_called_once()

    assert alerta.recebimentos_email.filter(
        usuario=usuario,
        data_ocorrencia=ocorrencia,
    ).count() == 1


def test_nao_envia_email_quando_recebimento_ja_existe(
    alerta, grupo, unidade_ue, criar_usuario,
    recebimento_email_alerta_pagina_factory
):
    usuario = criar_usuario(grupo, [unidade_ue])
    ocorrencia = date(2026, 11, 15)

    recebimento_email_alerta_pagina_factory(
        alerta=alerta,
        usuario=usuario,
        data_ocorrencia=ocorrencia,
    )

    with patch(
        f'{SERVICO}.enviar_email_nova_notificacao_v2'
    ) as mock_envio:
        resultado = AlertaPaginaEmailService.enviar_para_usuario(
            alerta.id, usuario.id, ocorrencia
        )

    assert resultado is False
    mock_envio.assert_not_called()
    assert alerta.recebimentos_email.count() == 1


def test_nao_registra_recebimento_quando_envio_falha(
    alerta, grupo, unidade_ue, criar_usuario
):
    usuario = criar_usuario(grupo, [unidade_ue])
    ocorrencia = date(2026, 11, 15)

    with patch(
        f'{SERVICO}.enviar_email_nova_notificacao_v2',
        side_effect=[False, True],
    ) as mock_envio:
        primeiro = AlertaPaginaEmailService.enviar_para_usuario(
            alerta.id, usuario.id, ocorrencia
        )

        assert primeiro is False
        assert not alerta.recebimentos_email.exists()

        segundo = AlertaPaginaEmailService.enviar_para_usuario(
            alerta.id, usuario.id, ocorrencia
        )

    assert segundo is True
    assert mock_envio.call_count == 2

    assert alerta.recebimentos_email.filter(
        usuario=usuario,
        data_ocorrencia=ocorrencia,
    ).count() == 1


def test_envia_novamente_em_outra_ocorrencia_anual(
    alerta, grupo, unidade_ue, criar_usuario
):
    usuario = criar_usuario(grupo, [unidade_ue])

    with patch(
        f'{SERVICO}.enviar_email_nova_notificacao_v2',
        return_value=True,
    ) as mock_envio:
        primeiro = AlertaPaginaEmailService.enviar_para_usuario(
            alerta.id, usuario.id, date(2026, 11, 15)
        )
        segundo = AlertaPaginaEmailService.enviar_para_usuario(
            alerta.id, usuario.id, date(2027, 11, 15)
        )

    assert primeiro is True
    assert segundo is True
    assert mock_envio.call_count == 2

    assert alerta.recebimentos_email.count() == 2
    assert set(
        alerta.recebimentos_email.values_list(
            'data_ocorrencia', flat=True
        )
    ) == {
        date(2026, 11, 15),
        date(2027, 11, 15),
    }
