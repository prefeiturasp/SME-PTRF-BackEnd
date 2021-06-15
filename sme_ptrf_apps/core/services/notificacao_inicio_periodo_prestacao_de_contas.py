import logging
from datetime import date
from sme_ptrf_apps.core.models import Periodo
from sme_ptrf_apps.users.services.permissions_service import get_users_by_permission
from django.db.models import Count

logger = logging.getLogger(__name__)


def notificar_inicio_periodo_prestacao_de_contas():
    logger.info(f'Notificar início período prestação de contas service')
    data_de_hoje = date.today()

    periodo = Periodo.objects.filter(data_inicio_prestacao_contas__lte=data_de_hoje,
                                     data_fim_prestacao_contas__gte=data_de_hoje).first()

    users = get_users_by_permission('access_receita')
    users = users.filter(visoes__nome="UE")
    users = users.annotate(c=Count('unidades')).filter(c__gt=0)

    if periodo and users:
        for user in users:
            logger.info(f"XXXXXX Usuario: {user.name} | Período: {periodo.data_inicio_prestacao_contas}")
