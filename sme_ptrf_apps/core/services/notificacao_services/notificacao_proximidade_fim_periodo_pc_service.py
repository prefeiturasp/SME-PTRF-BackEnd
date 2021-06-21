import logging
from datetime import date, timedelta
from sme_ptrf_apps.core.models import Periodo, Notificacao, Parametros
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from django.db.models import Count

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_proximidade_fim_periodo_prestacao_conta():
    logging.info("Criando notificações de proximidade do fim do período de prestação de contas...")
    dias_antes = Parametros.get().dias_antes_fim_periodo_pc_para_notificacao
    data_alvo = date.today() + timedelta(days=dias_antes)

    periodo = Periodo.objects.filter(
        data_fim_prestacao_contas__lte=data_alvo,
        data_fim_prestacao_contas__gte=date.today(),
        notificacao_proximidade_fim_pc_realizada=False
    ).first()

    users = get_users_by_permission('recebe_notificacao_proximidade_fim_periodo_prestacao_de_contas')

    if users:
        try:
            users = users.filter(visoes__nome="UE")
            users = users.annotate(c=Count('unidades')).filter(c__gt=0)
        except Exception:
            logger.error(f'Erro ao filtrar usuario por visão e ou unidade')

    if periodo:
        if users:
            for user in users:
                logger.info(f"Gerando notificação para o usuario: {user} | Período: {periodo.referencia}")

                dias_para_fim = periodo.data_fim_prestacao_contas - date.today()

                Notificacao.notificar(
                    tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                    categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
                    remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                    titulo=f"Últimos dias para enviar a PC {periodo.referencia}",
                    descricao=f"Faltam apenas {dias_para_fim.days} dia(s) para o término do período de prestações de contas. Envie a sua prestação de contas.",
                    usuario=user
                )
                periodo.notificacao_proximidade_fim_prestacao_de_contas_realizada()
        else:
            logger.info(f"Não foram encontrados usuários a serem notificados.")
    else:
        logger.info(f"Não foram encontrados períodos a serem notificados.")
