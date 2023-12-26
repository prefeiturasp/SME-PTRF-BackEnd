import logging
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

logger = logging.getLogger(__name__)

def notificar_pendencia_geracao_ata_apresentacao(prestacao_de_contas):
    logger.info(f'Iniciando a geração de notificação de pendência de geração de ata de apresentação da pc {prestacao_de_contas} service')

    usuarios = get_users_by_permission('recebe_notificacao_geracao_ata_apresentacao')
    usuarios = usuarios.filter(visoes__nome="UE", unidades__codigo_eol=prestacao_de_contas.associacao.unidade.codigo_eol)

    for usuario in usuarios:
        logger.info(f"Gerando notificação de pendência de geração de ata de apresentação para o usuario: {usuario}")

        Notificacao.notificar(
            tipo=Notificacao.TIPO_NOTIFICACAO_AVISO,
            categoria=Notificacao.CATEGORIA_NOTIFICACAO_GERACAO_ATA,
            remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
            titulo=f"Geração da ata de apresentação",
            descricao=f"A ata de apresentação da PC {prestacao_de_contas} não foi gerada e a DRE {prestacao_de_contas.associacao.unidade} não pode receber a PC. Favor efetuar a geração da ata.",
            usuario=usuario,
            renotificar=True,
            unidade=prestacao_de_contas.associacao.unidade,
            prestacao_conta=prestacao_de_contas,
            periodo=prestacao_de_contas.periodo,
        )

    logger.info(f'Finalizando a geração de notificação de pendência de geração de ata de apresentação.')
