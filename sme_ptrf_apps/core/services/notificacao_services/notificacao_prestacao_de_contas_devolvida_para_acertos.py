import logging
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from .formata_data_dd_mm_yyyy import formata_data_dd_mm_yyyy

logger = logging.getLogger(__name__)


def notificar_prestacao_de_contas_devolvida_para_acertos(prestacao_de_contas, data_limite_ue, enviar_email=True):
    logger.info(f'Iniciando a geração de notificação prestação de contas devolvida para acertos {prestacao_de_contas} service')

    users = get_users_by_permission('recebe_notificacao_prestacao_de_contas_devolvida_para_acertos')
    users = users.filter(visoes__nome="UE")
    associacao = prestacao_de_contas.associacao
    usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

    if usuarios:
        for usuario in usuarios:
            logger.info(f"Gerando notificação de PC devolvida para acerto para o usuario: {usuario} | Data Limite: {formata_data_dd_mm_yyyy(data_limite_ue)}")

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
                titulo=f"Ajustes necessários na PC | Prazo: {formata_data_dd_mm_yyyy(data_limite_ue)}",
                descricao=f"A DRE solicitou alguns ajustes em sua prestação de contas do período {prestacao_de_contas.periodo.referencia}. O seu prazo para envio das mudanças é {formata_data_dd_mm_yyyy(data_limite_ue)}",
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email,
                unidade=associacao.unidade,
                prestacao_conta=prestacao_de_contas,
            )

    logger.info(f'Finalizando a geração de notificação prestação de contas devolvida para acertos')
