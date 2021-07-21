import logging
from sme_ptrf_apps.users.services import SmeIntegracaoService
from sme_ptrf_apps.users.tasks import enviar_email_nova_notificacao_async

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def enviar_email_nova_notificacao(usuario=None, titulo=None, descricao=None):
    logger.info(f'Iniciando envio de email nova notificação service {usuario}')

    result = SmeIntegracaoService.informacao_usuario_sgp(usuario.username)

    logger.info(f'XXX EMAIL USUARIO {result}')

    if result['email']:
        try:
            enviar_email_nova_notificacao_async(email=result['email'], username=usuario.username, nome=usuario.name, titulo=titulo, descricao=descricao)
        except Exception as err:
            logger.info("Erro ao enviar email: %s", str(err))
            # raise ProblemaEnvioEmail("Problema ao enviar email.")


