import logging
from datetime import date, timedelta
from sme_ptrf_apps.core.models import Notificacao, Parametros, DevolucaoPrestacaoConta
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas(enviar_email=True):
    logging.info("Criando notificações de proximidade do fim do prazo de ajustes de prestação de contas service")
    dias_antes = Parametros.get().dias_antes_fim_prazo_ajustes_pc_para_notificacao
    data_alvo = date.today() + timedelta(days=dias_antes)

    users = get_users_by_permission('recebe_notificacao_proximidade_fim_prazo_ajustes_prestacao_de_contas')
    users = users.filter(visoes__nome="UE")

    devolucoes = DevolucaoPrestacaoConta.objects.filter(
        prestacao_conta__status="DEVOLVIDA",
        data_limite_ue__lte=data_alvo,
        data_limite_ue__gte=date.today(),
    ).order_by('-data_limite_ue')

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
                    logger.info(f"Gerando notificação de proximidade do fim do prazo de ajustes em PC para o usuário: {usuario} Devolução: {id_atual}")

                    dias_para_fim = devolucao.data_limite_ue - date.today()

                    # Gerando apenas 1 notificação por período e data ordenado decrescente por -data_limite_ue
                    Notificacao.notificar(
                        tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC,
                        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                        titulo=f"O prazo para envio dos ajustes da PC está se aproximando {prestacao_de_contas.periodo.referencia} | Prazo: {dias_para_fim.days} dia(s)",
                        descricao=f"Faltam apenas {dias_para_fim.days} dia(s) para o fim do prazo de envio dos ajustes de sua prestações de contas de {prestacao_de_contas.periodo.referencia}. Fique atento para não perder o prazo e realize os ajustes solicitados.",
                        usuario=usuario,
                        renotificar=False,
                        enviar_email=enviar_email,
                        unidade=associacao.unidade if associacao else None,
                        prestacao_conta=prestacao_de_contas,
                    )
    else:
        logger.info(f"Não foram encontrados prestações de contas próximas ao fim do prazo de envio de ajustes.")
