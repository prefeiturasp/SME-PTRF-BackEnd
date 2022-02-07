import datetime
import json

import pytest
from rest_framework import status

from ...models import AtaParecerTecnico

pytestmark = pytest.mark.django_db


def test_api_update_ata_associacao(jwt_authenticated_client_dre, ata_parecer_tecnico):
    payload = {
        "data_reuniao": "2020-06-20",
        "local_reuniao": "Sala XXX",
        "comentarios": "TesteXXX",
        "presentes_na_ata": []
    }

    response = jwt_authenticated_client_dre.patch(f'/api/ata-parecer-tecnico/{ata_parecer_tecnico.uuid}/', data=json.dumps(payload),
                            content_type='application/json')

    registro_alterado = AtaParecerTecnico.by_uuid(uuid=ata_parecer_tecnico.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.data_reuniao == datetime.date(2020, 6, 20)
    assert registro_alterado.local_reuniao == "Sala XXX"
    assert registro_alterado.comentarios == "TesteXXX"
