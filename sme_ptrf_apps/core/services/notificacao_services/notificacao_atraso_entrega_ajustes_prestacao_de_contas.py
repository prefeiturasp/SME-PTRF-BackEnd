import logging
from datetime import date
from sme_ptrf_apps.core.models import DevolucaoPrestacaoConta, Notificacao
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from .formata_data_dd_mm_yyyy import formata_data_dd_mm_yyyy

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_atraso_entrega_ajustes_prestacao_de_contas(enviar_email=True):
    logger.info(f'Iniciando a geração de notificação sobre atraso na entrega de ajustes de prestações de contas service')
    data_de_hoje = date.today()

    users = get_users_by_permission('recebe_notificacao_atraso_entrega_ajustes_prestacao_de_contas')
    users = users.filter(visoes__nome="UE")

    devolucoes = DevolucaoPrestacaoConta.objects.filter(prestacao_conta__status="DEVOLVIDA", data_limite_ue__lt=data_de_hoje).order_by('-data_limite_ue')

    if devolucoes:
        for devolucao in devolucoes:
            prestacao_de_contas = devolucao.prestacao_conta
            associacao = prestacao_de_contas.associacao
            usuarios = users.filter(unidades__codigo_eol=associacao.unidade.codigo_eol)

            devolucao_mais_recente_da_pc = prestacao_de_contas.devolucoes_da_prestacao.order_by('-id').first()

            id_atual = devolucao.id if devolucao else ""
            logger.info(f"Verificando devolução {id_atual} da PC:{prestacao_de_contas} Associação:{associacao}...")

            if devolucao != devolucao_mais_recente_da_pc:
                id_mais_recente = devolucao_mais_recente_da_pc.id if devolucao_mais_recente_da_pc else ""
                logger.info(f"Ignorando devolução {id_atual} por não ser a mais recente. Mais recente:{id_mais_recente}.")
                continue

            if usuarios:
                for usuario in usuarios:
                    logger.info(f"Gerando notificação de atraso na entrega de ajustes de PC para o usuario: {usuario} Devolução: {id_atual}")

                    # Gerando apenas 1 notificação por período e data ordenado decrescente por -data_limite_ue
                    Notificacao.notificar(
                        tipo=Notificacao.TIPO_NOTIFICACAO_ALERTA,
                        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC,
                        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                        titulo=f"Devolução de ajustes na PC atrasada {prestacao_de_contas.periodo.referencia}",
                        descricao=f"Sua unidade ainda não enviou os ajustes "
                                  f"solicitados pela DRE em sua prestação de contas do período "
                                  f"{prestacao_de_contas.periodo.referencia}. "
                                  f"O seu prazo era {formata_data_dd_mm_yyyy(devolucao.data_limite_ue)}",
                        usuario=usuario,
                        renotificar=False,
                        enviar_email=enviar_email,
                        unidade=associacao.unidade if associacao else None,
                        prestacao_conta=prestacao_de_contas,
                    )
    else:
        logger.info(f"Não foram encontrados prestações de contas a serem notificadas.")


