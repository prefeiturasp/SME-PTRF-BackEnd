from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task

from sme_ptrf_apps.core.services.enviar_email import enviar_email_html

env = environ.Env()

@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_redifinicao_senha(email, username, nome, hash_definicao):
    link = f"http://{env('SERVER_NAME')}/#/login/?hash={hash_definicao}"
    context = {
        'url': link,
        'nome': nome,
        'login': username
    }
    return enviar_email_html(
        assunto='Solicitação de redefinição de senha',
        template='email_redefinicao_senha.html',
        context=context,
        enviar_para=email
    )
