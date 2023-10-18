from datetime import date
import logging
from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task

from sme_ptrf_apps.core.services.enviar_email import enviar_email_nova_notificacao_html

env = environ.Env()
logger = logging.getLogger(__name__)

@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_nova_notificacao_async(email, username, nome, titulo, descricao):
    logger.info("Tarefa de envio de email nova notificacao async")
    link = f"https://{env('SERVER_NAME')}/"
    data = date.today().strftime("%d/%m/%Y")
    context = {
        'url': link,
        'nome': nome,
        'login': username,
        'descricao': descricao,
        'server_name': f"https://{env('SERVER_NAME')}",
        'data': data
    }
    return enviar_email_nova_notificacao_html(
        assunto=titulo,
        template='email_nova_notificacao.html',
        context=context,
        enviar_para=email
    )