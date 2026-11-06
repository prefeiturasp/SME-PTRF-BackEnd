from celery import shared_task

from sme_ptrf_apps.core.services.alerta_pagina_email_service import AlertaPaginaEmailService


@shared_task(
    time_limit=30,
    soft_time_limit=25,
    acks_late=True,
    rate_limit='10/s'
)
def enviar_email_alerta_pagina_usuario_async(alerta_id, usuario_id, data_ocorrencia):
    """Enviar o e-mail do alerta para um usuário. Retorna ``False`` se alerta ou usuário não existirem."""
    AlertaPaginaEmailService.enviar_para_usuario(alerta_id, usuario_id, data_ocorrencia)


@shared_task
def enviar_emails_alertas_paginas_async():
    """Recupera todos os itens para envio e dispara entre tasks individuais"""
    disparos = AlertaPaginaEmailService.registrar_disparos_do_dia()
    for alerta_id, usuario_id, data_ocorrencia in disparos:
        enviar_email_alerta_pagina_usuario_async.delay(
            alerta_id,
            usuario_id,
            data_ocorrencia
        )
    return len(disparos)
