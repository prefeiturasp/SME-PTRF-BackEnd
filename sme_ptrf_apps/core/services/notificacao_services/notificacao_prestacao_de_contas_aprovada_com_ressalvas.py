import logging
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

logger = logging.getLogger(__name__)


def notificar_prestacao_de_contas_aprovada_com_ressalvas(prestacao_de_contas, motivos_aprovacao_ressalva,
                                                         outros_motivos_aprovacao_ressalva, enviar_email=True):

    logger.info(f'Iniciando a geração de notificação prestação de contas aprovada com ressalvas {prestacao_de_contas} service')

    users = get_users_by_permission('recebe_notificacao_aprovacao_pc')
    users = users.filter(visoes__nome="UE")
    associacao = prestacao_de_contas.associacao
    usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

    motivos_aprovacao_ressalva_notificacao = ""
    for motivo in motivos_aprovacao_ressalva:
        motivos_aprovacao_ressalva_notificacao = f"{motivos_aprovacao_ressalva_notificacao} {motivo} \n"

    if usuarios:
        for usuario in usuarios:
            logger.info(f"Gerando notificação de PC Aprovada com Ressalvas para o usuario: {usuario}")

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_APROVACAO_RESSALVAS_PC,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                titulo=f"A PC do período {prestacao_de_contas.periodo.referencia} foi aprovada com ressalvas pela DRE",
                descricao=f"A prestação de contas referente ao período {prestacao_de_contas.periodo.referencia} foi aprovada com ressalvas pelos seguintes motivos: {motivos_aprovacao_ressalva_notificacao} {outros_motivos_aprovacao_ressalva}",
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email,
                unidade=associacao.unidade,
                prestacao_conta=prestacao_de_contas,
            )

    logger.info(f'Finalizando a geração de notificação prestação de contas aprovada com ressalvas')
