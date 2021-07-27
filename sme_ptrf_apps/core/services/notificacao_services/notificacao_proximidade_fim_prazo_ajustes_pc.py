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

            if usuarios:
                for usuario in usuarios:
                    logger.info(f"Gerando notificação de atraso na entrega de ajustes de PC para o usuario: {usuario}")

                    dias_para_fim = devolucao.data_limite_ue - date.today()

                    # Gerando apenas 1 notificação por período e data ordenado decrescente por -data_limite_ue
                    Notificacao.notificar(
                        tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ANALISE_PC,
                        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                        titulo=f"O prazo para envio dos ajustes da PC está se aproximando {prestacao_de_contas.periodo.referencia}",
                        descricao=f"Faltam apenas {dias_para_fim.days} dia(s) para o fim do prazo de envio dos ajustes de sua prestações de contas de {prestacao_de_contas.periodo.referencia}. Fique atento para não perder o prazo e realize os ajustes solicitados.",
                        usuario=usuario,
                        renotificar=False,
                        enviar_email=enviar_email
                    )
    else:
        logger.info(f"Não foram encontrados prestações de contas a serem notificadas.")
