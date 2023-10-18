from datetime import date
import logging
from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task
from config import celery_app

from sme_ptrf_apps.core.services.enviar_email import enviar_email_html, enviar_email_nova_notificacao_html

env = environ.Env()
logger = logging.getLogger(__name__)

""" @shared_task(
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
    ) """


""" @shared_task(
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
    ) """


""" @celery_app.task()
def get_users_count():
    # A pointless Celery task to demonstrate usage.
    from django.contrib.auth import get_user_model
    return get_user_model().objects.count() """
