import json

import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_exclui_paa(jwt_authenticated_client_sme, flag_paa, paa):
    response = jwt_authenticated_client_sme.delete(f"/api/paa/{paa.uuid}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT