import pytest
from unittest.mock import patch

from ....core.models import Notificacao

pytestmark = pytest.mark.django_db

def test_notificar_deve_enviar_email(usuario_notificavel, monkeypatch):
    monkeypatch.setenv('SERVER_NAME', 'sig-escola.sme.prefeitura.sp.gov.br')
    
    path = 'sme_ptrf_apps.core.services.notificacao_services.enviar_email_notificacao.enviar_email_nova_notificacao'

    with patch(path) as mock_enviar_email:
        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
            titulo=f"Notificacao teste",
            descricao=f"Descricao teste",
            usuario=usuario_notificavel,
            renotificar=False,
            enviar_email=True,
        )
        mock_enviar_email.assert_called_once_with(usuario=usuario_notificavel, titulo='Notificacao teste', descricao="Descricao teste")


def test_nao_notificar_deve_enviar_email_se_estiver_fora_de_ambiente_de_producao(usuario_notificavel, monkeypatch):
    monkeypatch.setenv('SERVER_NAME', 'um_server_name_qualquer')
    
    path = 'sme_ptrf_apps.core.services.notificacao_services.enviar_email_notificacao.enviar_email_nova_notificacao'

    with patch(path) as mock_enviar_email:
        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
            titulo=f"Notificacao teste",
            descricao=f"Descricao teste",
            usuario=usuario_notificavel,
            renotificar=False,
            enviar_email=True,
        )
        mock_enviar_email.assert_not_called()