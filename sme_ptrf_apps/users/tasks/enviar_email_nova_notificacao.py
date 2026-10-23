from datetime import date
import logging
from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task

from sme_ptrf_apps.core.services.enviar_email import enviar_email_nova_notificacao_html

env = environ.Env()
logger = logging.getLogger(__name__)

TEMPLATE_EMAIL_NOVA_NOTIFICACAO = 'email_nova_notificacao.html'


def contexto_email_nova_notificacao(username, nome, descricao):
    """Monta o contexto do template de e-mail de nova notificação."""
    server_name = f"https://{env('SERVER_NAME')}"
    return {
        'url': f"{server_name}/",
        'nome': nome,
        'login': username,
        'descricao': descricao,
        'server_name': server_name,
        'data': date.today().strftime("%d/%m/%Y"),
    }


@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_nova_notificacao_async(email, username, nome, titulo, descricao):
    logger.info("Tarefa de envio de email nova notificacao async")

    return enviar_email_nova_notificacao_html(
        assunto=titulo,
        template='email_nova_notificacao.html',
        context=contexto_email_nova_notificacao(username, nome, descricao),
        enviar_para=email
    )
