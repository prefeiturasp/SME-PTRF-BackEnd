from datetime import date
import json
import pytest

from rest_framework import status

from sme_ptrf_apps.paa.models import PeriodoPaa


pytestmark = pytest.mark.django_db


def test_pdelete_sucesso(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    assert PeriodoPaa.objects.count() == 1

    response = jwt_authenticated_client_sme.delete(f'/api/periodos-paa/{periodo_paa_1.uuid}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert PeriodoPaa.objects.count() == 0


def test_delete_404(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    assert PeriodoPaa.objects.count() == 1

    response = jwt_authenticated_client_sme.delete(f'/api/periodos-paa/b737979c-66e2-4d38-b266-652aa1f0fe5d/')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert PeriodoPaa.objects.count() == 1
