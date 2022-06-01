import logging
from datetime import date

from django.contrib.auth import get_user_model
from sme_ptrf_apps.core.models import (
    ComentarioAnalisePrestacao,
    Notificacao,
    Periodo,
    Associacao
)
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_comentario_pc(dado, enviar_email=True):
    logging.info("Criando notificações de comentário.")

    periodo = Periodo.by_uuid(dado['periodo'])
    comentarios = [ComentarioAnalisePrestacao.by_uuid(uuid) for uuid in dado['comentarios']]

    associacao = Associacao.by_uuid(dado['associacao'])

    tipo = Notificacao.TIPO_NOTIFICACAO_AVISO
    categoria = Notificacao.CATEGORIA_NOTIFICACAO_COMENTARIO_PC
    remetente = Notificacao.REMETENTE_NOTIFICACAO_DRE
    titulo = f"Comentário feito em sua prestação de contas de {periodo.referencia}."

    # Define destinatários
    users = get_users_by_permission('recebe_notificacao_comentario_em_pc')
    usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

    if 'enviar_email' in dado:
        enviar_email = dado['enviar_email']

    for usuario in usuarios:
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
                unidade=associacao.unidade,
            )

            comentario.set_comentario_notificado()

        logger.info("Notificações criadas com sucesso.")
