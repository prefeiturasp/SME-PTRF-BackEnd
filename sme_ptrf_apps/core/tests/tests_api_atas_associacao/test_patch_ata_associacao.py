import json
import pytest
from rest_framework import status
from model_bakery import baker
from ...models import Participante

pytestmark = pytest.mark.django_db


@pytest.fixture
def participante_ata_professor_gremio(ata_2020_1_cheque_aprovada):
    return baker.make(
        'Participante',
        ata=ata_2020_1_cheque_aprovada,
        identificacao="123",
        nome="membro",
        cargo="teste cargo",
        membro=False,
        conselho_fiscal=False,
        professor_gremio=True
    )


def test_api_update_participante_professor_gremio(
    jwt_authenticated_client_a,
    ata_2020_1_cheque_aprovada,
    participante_ata_professor_gremio
):

    payload = {
        "presentes_na_ata": [
            {
                "ata": str(ata_2020_1_cheque_aprovada.uuid),
                "identificacao": participante_ata_professor_gremio.identificacao,
                "nome": participante_ata_professor_gremio.nome,
                "cargo": participante_ata_professor_gremio.cargo,
                "membro": participante_ata_professor_gremio.membro,
                "presente": participante_ata_professor_gremio.presente,
                "professor_gremio": True,
            }
        ]
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/atas-associacao/{ata_2020_1_cheque_aprovada.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    registro = Participante.objects.get(
        ata=ata_2020_1_cheque_aprovada,
        identificacao=participante_ata_professor_gremio.identificacao
    )

    assert response.status_code == status.HTTP_200_OK
    assert registro.professor_gremio is True
