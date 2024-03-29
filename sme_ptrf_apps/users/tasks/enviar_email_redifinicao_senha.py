from datetime import date
import logging
from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task

from sme_ptrf_apps.core.services.enviar_email import enviar_email_html

env = environ.Env()
logger = logging.getLogger(__name__)

@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_redifinicao_senha(email, username, nome, hash_definicao):
    logger.info("Tarefa de envio de email")
    link = f"https://{env('SERVER_NAME')}/redefinir-senha/{hash_definicao}"
    data = date.today().strftime("%d/%m/%Y")
    context = {
        'url': link,
        'nome': nome,
        'login': username,
        'server_name': f"https://{env('SERVER_NAME')}",
        'data': data
    }
    return enviar_email_html(
        assunto='Solicitação de redefinição de senha',
        template='email_redefinicao_senha.html',
        context=context,
        enviar_para=email
    )