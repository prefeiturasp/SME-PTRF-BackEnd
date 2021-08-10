import pytest
from unittest.mock import patch

from ....core.models import Notificacao

pytestmark = pytest.mark.django_db


def test_notificar_deve_enviar_email(usuario_notificavel):
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
            enviar_email=True
        )
        mock_enviar_email.assert_called_once_with(usuario=usuario_notificavel, titulo='Notificacao teste', descricao="Descricao teste")


