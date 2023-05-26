import pytest
import json
from rest_framework import status
from freezegun import freeze_time
from unittest.mock import patch

pytestmark = pytest.mark.django_db


def test_devolver_consolidado(
    jwt_authenticated_client_sme,
    consolidado_dre_teste_api_consolidado_dre,
):
    payload = {
        'data_limite': '2023-07-01',
    }

    with patch('sme_ptrf_apps.dre.models.consolidado_dre.ConsolidadoDRE.devolver_consolidado') as mock_devolver_consolidado:

        response = jwt_authenticated_client_sme.patch(
            f'/api/consolidados-dre/{consolidado_dre_teste_api_consolidado_dre.uuid}/devolver-consolidado/',
            data=json.dumps(payload),
            content_type='application/json',
        )

        mock_devolver_consolidado.return_value = None

        assert response.status_code == status.HTTP_200_OK
        mock_devolver_consolidado.assert_called_once()


def test_devolver_consolidado_requer_data_limite(
    jwt_authenticated_client_sme,
    consolidado_dre_teste_api_consolidado_dre,
):
    with patch('sme_ptrf_apps.dre.models.consolidado_dre.ConsolidadoDRE.devolver_consolidado') as mock_devolver_consolidado:

        response = jwt_authenticated_client_sme.patch(
            f'/api/consolidados-dre/{consolidado_dre_teste_api_consolidado_dre.uuid}/devolver-consolidado/',
            content_type='application/json'
        )

        mock_devolver_consolidado.return_value = None

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {'data_limite': ['This field is required.']}


@freeze_time("2022-10-29 10:33:50")
def test_devolver_consolidado_requer_data_limite_igual_ou_posterior_a_hoje(
    jwt_authenticated_client_sme,
    consolidado_dre_teste_api_consolidado_dre,
):
    payload = {
        'data_limite': '2022-10-12',   # Data anterior à data de "hoje" 29/10/2022
    }

    with patch('sme_ptrf_apps.dre.models.consolidado_dre.ConsolidadoDRE.devolver_consolidado') as mock_devolver_consolidado:

        response = jwt_authenticated_client_sme.patch(
            f'/api/consolidados-dre/{consolidado_dre_teste_api_consolidado_dre.uuid}/devolver-consolidado/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        mock_devolver_consolidado.return_value = None

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {'data_limite': ['Data limite precisa ser posterior a hoje (2022-10-29).']}
