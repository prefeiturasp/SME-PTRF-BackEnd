import logging
from sme_ptrf_apps.core.models import Notificacao
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Q

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_prestacao_de_contas_reprovada(prestacao_de_contas, motivos_reprovacao,
                                                         outros_motivos_reprovacao, enviar_email=True):

    logger.info(f'Iniciando a geração de notificação prestação de contas reprovada {prestacao_de_contas} service')

    perm_nao_incluindo_motivos = Permission.objects.get(codename='recebe_notificacao_reprovacao_pc_nao_incluindo_motivos')
    perm_incluindo_motivos = Permission.objects.get(codename='recebe_notificacao_reprovacao_pc_incluindo_motivos')

    users = User.objects.filter(
        Q(user_permissions=perm_nao_incluindo_motivos) |
        Q(user_permissions=perm_incluindo_motivos) |
        Q(groups__permissions=perm_nao_incluindo_motivos) |
        Q(groups__permissions=perm_incluindo_motivos)
    ).distinct()

    users = users.filter(visoes__nome="UE")
    associacao = prestacao_de_contas.associacao
    usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

    motivos_reprovacao_notificacao = ""
    for motivo in motivos_reprovacao:
        motivos_reprovacao_notificacao = f"{motivos_reprovacao_notificacao} {motivo} \n"

    if usuarios:
        for usuario in usuarios:
            logger.info(f"Gerando notificação de PC Reprovada para o usuario: {usuario}")

            if usuario.has_perm('core.recebe_notificacao_reprovacao_pc_incluindo_motivos'):
                descricao_notificacao = f"A prestação de contas referente ao período {prestacao_de_contas.periodo.referencia} foi reprovada pelos seguintes motivos: {motivos_reprovacao_notificacao} {outros_motivos_reprovacao}"
            else:
                descricao_notificacao = f"A prestação de contas referente ao período {prestacao_de_contas.periodo.referencia} foi reprovada."

            Notificacao.notificar(
                tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                categoria=Notificacao.CATEGORIA_NOTIFICACAO_REPROVACAO_PC,
                remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                titulo=f"A PC do período {prestacao_de_contas.periodo.referencia} foi reprovada pela DRE",
                descricao=descricao_notificacao,
                usuario=usuario,
                renotificar=True,
                enviar_email=enviar_email,
                unidade=associacao.unidade,
                prestacao_conta=prestacao_de_contas,
            )

    logger.info(f'Finalizando a geração de notificação prestação de contas reprovada')
