from datetime import date
import pytest
import logging

from unittest.mock import MagicMock
from sme_ptrf_apps.sme.services.exporta_dados_unidades_service import (
    ExportacoesDadosUnidadesService
)
from django.contrib.auth import get_user_model
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db

DATAS = (date(2020, 3, 26), date(2024, 4, 26))


@pytest.fixture
def mock_query_set():
    queryset = MagicMock()
    queryset.filter.return_value = queryset
    return queryset


@pytest.fixture
def usuario_teste():
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.save()
    return user


@pytest.fixture
def export_service(mock_query_set, usuario_teste):
    return ExportacoesDadosUnidadesService(
        queryset=mock_query_set,
        data_inicio="2023-01-01",
        data_final="2023-12-31",
        nome_arquivo="unidades",
        user=usuario_teste,
    )
