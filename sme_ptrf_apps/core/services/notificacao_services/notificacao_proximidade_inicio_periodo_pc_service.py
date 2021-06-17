import logging
from datetime import date, timedelta
from sme_ptrf_apps.core.models import Periodo, Notificacao, Parametros
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from django.db.models import Count

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_proximidade_inicio_periodo_prestacao_conta():
    logging.info("Criando notificações de proximidade do inicio do período de prestação de contas...")
    dias_antes = Parametros.get().dias_antes_inicio_periodo_pc_para_notificacao
    data_alvo = date.today() + timedelta(days=dias_antes)

    periodo = Periodo.objects.filter(
        data_inicio_prestacao_contas__lte=data_alvo,
        data_fim_prestacao_contas__gte=data_alvo,
        notificacao_proximidade_inicio_pc_realizada=False
    ).first()

    users = get_users_by_permission('recebe_notificacao_proximidade_inicio_prestacao_de_contas')

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

                dias_para_inicio = periodo.data_inicio_prestacao_contas - date.today()

                Notificacao.notificar(
                    tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                    categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
                    remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                    titulo=f"O período de envio da PC de {periodo.referencia} está se aproximando.",
                    descricao=f"Faltam apenas {dias_para_inicio.days} dias para o início do período de prestações "
                              f"de contas. Finalize o cadastro de crédito e de gastos, a conciliação bancária e "
                              f"gere os documentos da prestação de contas.",
                    usuario=user
                )
                periodo.notificacao_proximidade_inicio_prestacao_de_contas_realizada()
        else:
            logger.info(f"Não foram encontrados usuários a serem notificados.")
    else:
        logger.info(f"Não foram encontrados períodos a serem notificados.")
