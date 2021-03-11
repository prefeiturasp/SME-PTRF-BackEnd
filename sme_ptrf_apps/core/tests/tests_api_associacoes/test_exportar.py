import json

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

pytestmark = pytest.mark.django_db


def test_exportar(jwt_authenticated_client_a, associacao):
    url = f"/api/associacoes/{associacao.uuid}/exportar/"
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=associacao.xlsx'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
