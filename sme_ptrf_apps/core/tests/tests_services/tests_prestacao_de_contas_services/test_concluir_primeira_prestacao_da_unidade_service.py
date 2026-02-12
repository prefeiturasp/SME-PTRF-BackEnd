import pytest
from unittest.mock import patch, Mock
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService
pytestmark = pytest.mark.django_db


def test_validar_pc_sem_periodo_anterior_retorna_true(
    periodo,
    associacao,
    django_user_model
):
    user = django_user_model.objects.create_user(
        username="teste", password="123456"
    )

    fake_logger = Mock()

    with patch(
        "sme_ptrf_apps.logging.loggers.ContextualLogger.get_logger",
        return_value=fake_logger,
    ):

        pc_service = PrestacaoContaService(
            periodo_uuid=periodo.uuid,
            associacao_uuid=associacao.uuid,
            username=user.username,
            logger=fake_logger,
        )

        assert pc_service.validar_geracao_pc_periodo_anterior() is True
