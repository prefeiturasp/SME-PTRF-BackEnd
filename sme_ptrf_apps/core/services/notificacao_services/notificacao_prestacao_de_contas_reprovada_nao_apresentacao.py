import logging
from sme_ptrf_apps.core.models import Notificacao
from django.contrib.auth import get_user_model
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_prestacao_de_contas_reprovada_nao_apresentacao(prestacao_de_contas, enviar_email=True):

    logger.info(f'Iniciando a geração de notificação prestação de contas reprovada não apresentação {prestacao_de_contas} service')

    users = get_users_by_permission('recebe_notificacao_conclusao_reprovada_pc_nao_apresentada')
    users = users.filter(visoes__nome="UE")
    associacao = prestacao_de_contas.associacao
    usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

    if usuarios:
        for usuario in usuarios:
            logger.info(f"Gerando notificação de PC Reprovada Por Não Apreserntação para o usuario: {usuario}")

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_CONCLUSAO_PC,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
                titulo=f"Conclusão da PC como reprovada por não apresentação",
                descricao=f"A PC {prestacao_de_contas.periodo.referencia} foi concluída como reprovada pois não foi apresentada.",
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email,
                unidade=associacao.unidade,
            )

    logger.info(f'Finalizando a geração de notificação prestação de contas reprovada por não apresentação')
