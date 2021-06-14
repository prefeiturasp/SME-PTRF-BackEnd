import logging

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_proximidade_inicio_periodo_prestacao_conta():
    logging.info("Criando notificações de proximidade do inicio do período de prestação de contas...")
