import logging

from des.models import DynamicEmailConfiguration
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def enviar_email_html(assunto, template, context, enviar_para):
    logger.info('Enviando email para %s', enviar_para)
    try:
        config = DynamicEmailConfiguration.get_solo()
        conteudo = render_to_string(template_name=f'email/{template}', context=context)
        logger.info(config.from_email)
        email = EmailMessage(
            subject=assunto,
            body=conteudo,
            from_email=config.from_email or None,
            bcc=(enviar_para,),
            connection=EmailBackend(**config.__dict__)
        )
        email.content_subtype = 'html'
        email.send()
    except Exception as err:
        logger.info("Erro email: %s", str(err))


def enviar_email_nova_notificacao_html(assunto, template, context, enviar_para):

    logger.info('Enviando email de nova notificação para %s', enviar_para)

    try:
        config = DynamicEmailConfiguration.get_solo()
        conteudo = render_to_string(template_name=f'email/{template}', context=context)
        logger.info(config.from_email)
        email = EmailMessage(
            subject=assunto,
            body=conteudo,
            from_email=config.from_email or None,
            bcc=(enviar_para,),
            connection=EmailBackend(**config.__dict__)
        )
        email.content_subtype = 'html'
        email.send()
    except Exception as err:
        logger.info("Erro email: %s", str(err))
