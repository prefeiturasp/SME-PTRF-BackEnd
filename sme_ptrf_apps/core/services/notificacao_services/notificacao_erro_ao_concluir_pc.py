import logging
from sme_ptrf_apps.core.models import Notificacao

logger = logging.getLogger(__name__)


def notificar_erro_ao_concluir_pc(prestacao_de_contas, usuario, associacao, periodo, enviar_email=False):
    logger.info(f'Iniciando a geração de notificação de erro ao concluir pc {prestacao_de_contas} service')

    if usuario:
        logger.info(f"Gerando notificação de erro ao concluir PC para o usuario: {usuario}")

        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_URGENTE,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_ERRO_AO_CONCLUIR_PC,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
            titulo=f"Erro ao concluir PC do período {periodo.referencia}",
            descricao=f"Ocorreu um erro ao concluir a PC do período {periodo.referencia} da associação {associacao}, tente novamente",
            usuario=usuario,
            renotificar=True,
            enviar_email=enviar_email,
            unidade=associacao.unidade,
            prestacao_conta=prestacao_de_contas,
            periodo=periodo,
        )

    logger.info(f'Finalizando a geração de notificação de erro ao concluir PC')
