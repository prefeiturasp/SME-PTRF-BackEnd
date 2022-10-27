import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_devolver_consolidado(
    jwt_authenticated_client_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.dre.models.consolidado_dre.ConsolidadoDRE.devolver_consolidado') as mock_devolver_consolidado:

        response = jwt_authenticated_client_dre.patch(
            f'/api/consolidados-dre/{consolidado_dre_teste_api_consolidado_dre.uuid}/devolver-consolidado/',
            content_type='application/json'
        )

        mock_devolver_consolidado.return_value = None

        assert response.status_code == status.HTTP_200_OK
        mock_devolver_consolidado.assert_called_once()
