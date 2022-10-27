import logging
from sme_ptrf_apps.users.services import SmeIntegracaoService
from sme_ptrf_apps.users.tasks import enviar_email_nova_notificacao_async

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def enviar_email_nova_notificacao(usuario=None, titulo=None, descricao=None):
    logger.info(f'Iniciando envio de email nova notificação service para o usuário: {usuario}')

    result = SmeIntegracaoService.informacao_usuario_sgp(usuario.username)

    if result['email']:
        try:
            enviar_email_nova_notificacao_async(email=result['email'], username=usuario.username, nome=usuario.name,
                                                titulo=titulo, descricao=descricao)
            logger.info(f'Enviado email de notificação para o usuário: {usuario}')
        except Exception as err:
            logger.error("Erro ao enviar email: %s", str(err))
    else:
        logger.warning(f'O usuário {usuario} não tem e-mail cadastrado no CoreSSO. E-mail de notificação não enviado.')
