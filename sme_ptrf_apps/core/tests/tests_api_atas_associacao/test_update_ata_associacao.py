import datetime
import json

import pytest
from rest_framework import status

from ...models import Ata

pytestmark = pytest.mark.django_db


def test_api_update_ata_associacao(client, ata_2020_1_cheque_aprovada):

    payload = {
        "tipo_reuniao": "EXTRAORDINARIA",
        "convocacao": "SEGUNDA",
        "data_reuniao": "2020-06-20",
        "local_reuniao": "Sala XXX",
        "presidente_reuniao": "PedroXXX",
        "cargo_presidente_reuniao": "PresidenteXXX",
        "secretario_reuniao": "MariaXXX",
        "cargo_secretaria_reuniao": "SecretáriaXXX",
        "parecer_conselho": "REJEITADA",
        "comentarios": "TesteXXX",
    }

    response = client.patch(f'/api/atas-associacao/{ata_2020_1_cheque_aprovada.uuid}/', data=json.dumps(payload),
                            content_type='application/json')

    registro_alterado = Ata.by_uuid(uuid=ata_2020_1_cheque_aprovada.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.tipo_reuniao == 'EXTRAORDINARIA'
    assert registro_alterado.convocacao == "SEGUNDA"
    assert registro_alterado.data_reuniao == datetime.date(2020, 6, 20)
    assert registro_alterado.local_reuniao == "Sala XXX"
    assert registro_alterado.presidente_reuniao == "PedroXXX"
    assert registro_alterado.cargo_presidente_reuniao == "PresidenteXXX"
    assert registro_alterado.secretario_reuniao == "MariaXXX"
    assert registro_alterado.cargo_secretaria_reuniao == "SecretáriaXXX"
    assert registro_alterado.parecer_conselho == "REJEITADA"
    assert registro_alterado.comentarios == "TesteXXX"
