import logging
from datetime import date
from sme_ptrf_apps.core.models import DevolucaoPrestacaoConta, Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from .formata_data_dd_mm_yyyy import formata_data_dd_mm_yyyy

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_teste_envio_de_email():
    logger.info(f'XXXXX Iniciando a geração de notificação TESTE ENVIO DE EMAIL XXXXXX')

    users = get_users_by_permission('recebe_notificacao_atraso_entrega_ajustes_prestacao_de_contas')
    users = users.filter(username=6347959)

    if users:
        for usuario in users:
            logger.info(f"Gerando notificação de atraso na entrega de ajustes de PC para o usuario: {usuario}")

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                titulo=f"Titulo Notificacao TESTE ENVIO DE EMAIL",
                descricao=f"Descrição Notificacao TESTE ENVIO DE EMAIL",
                usuario=usuario,
                renotificar=True,
            )


