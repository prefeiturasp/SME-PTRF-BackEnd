import logging
from datetime import date

from django.contrib.auth import get_user_model
from sme_ptrf_apps.core.models import (
    ComentarioAnalisePrestacao,
    Notificacao,
    Periodo,
)
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_comentario_pc(dado, enviar_email=True):
    logging.info("Criando notificações.")

    periodo = Periodo.by_uuid(dado['periodo'])
    comentarios = [ComentarioAnalisePrestacao.by_uuid(uuid) for uuid in dado['comentarios']]

    tipo = Notificacao.TIPO_NOTIFICACAO_AVISO
    categoria = Notificacao.CATEGORIA_NOTIFICACAO_COMENTARIO_PC
    remetente = Notificacao.REMETENTE_NOTIFICACAO_DRE
    titulo = f"Comentário feito em sua prestação de contas de {periodo.referencia}."

    # Define destinatários
    usuarios_com_permissao = get_users_by_permission('recebe_notificacao_comentario_em_pc')

    if 'enviar_email' in dado:
        enviar_email = dado['enviar_email']

    for usuario in usuarios_com_permissao:
        for comentario in comentarios:
            Notificacao.notificar(
                tipo=tipo,
                categoria=categoria,
                remetente=remetente,
                titulo=titulo,
                descricao=comentario.comentario,
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email,
            )
        logger.info("Notificações criadas com sucesso.")
