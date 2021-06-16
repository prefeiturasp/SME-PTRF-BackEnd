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
        data_inicio_prestacao_contas__lte=data_de_hoje,
        data_fim_prestacao_contas__gte=data_de_hoje,
        notificacao_inicio_periodo_pc_realizada=False
    ).first()

    users = get_users_by_permission('recebe_notificacao_inicio_periodo_prestacao_de_contas')

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

                Notificacao.notificar(
                    tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
                    categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
                    remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
                    titulo=f"O período de envio da PC de {periodo.referencia} começou",
                    descricao="O período de prestações de contas já foi iniciado. Fique atento para não perder o prazo e envie os documentos da prestação de contas",
                    usuario=user
                )
                periodo.notificacao_inicio_prestacao_de_contas_realizada()
        else:
            logger.info(f"Não foram encontrados usuários a serem notificados sobre início do período de prestação de contas")
    else:
        logger.info(f"Não foram encontrados períodos a serem notificados sobre início do período de prestação de contas")
