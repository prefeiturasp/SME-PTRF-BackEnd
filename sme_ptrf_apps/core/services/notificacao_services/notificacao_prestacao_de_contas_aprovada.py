import logging
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

logger = logging.getLogger(__name__)


def notificar_prestacao_de_contas_aprovada(prestacao_de_contas, enviar_email=True):
    logger.info(f'Iniciando a geração de notificação prestação de contas aprovada {prestacao_de_contas} service')

    users = get_users_by_permission('recebe_notificacao_aprovacao_pc')
    users = users.filter(visoes__nome="UE")
    associacao = prestacao_de_contas.associacao
    usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

    if usuarios:
        for usuario in usuarios:
            logger.info(f"Gerando notificação de PC Aprovada para o usuario: {usuario}")

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_APROVACAO_PC,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                titulo=f"A PC do período {prestacao_de_contas.periodo.referencia} foi aprovada pela DRE",
                descricao=f"A prestação de contas referente ao período {prestacao_de_contas.periodo.referencia} foi aprovada",
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email,
                unidade=associacao.unidade,
                prestacao_conta=prestacao_de_contas,
            )

    logger.info(f'Finalizando a geração de notificação prestação de contas aprovada')
