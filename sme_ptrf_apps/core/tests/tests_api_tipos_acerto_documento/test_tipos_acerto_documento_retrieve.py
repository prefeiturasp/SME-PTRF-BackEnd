import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_tipo_acerto_documento(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01,
    tipo_documento_prestacao_conta_relacao_bens
):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-documento/{tipo_acerto_documento_01.uuid}/',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        'ativo': tipo_acerto_documento_01.ativo,
        'categoria': tipo_acerto_documento_01.categoria,
        'id': tipo_acerto_documento_01.id,
        'nome': tipo_acerto_documento_01.nome,
        'uuid': f'{tipo_acerto_documento_01.uuid}',
        'tipos_documento_prestacao': [
            {
                'documento_por_conta': tipo_documento_prestacao_conta_relacao_bens.documento_por_conta,
                'id': tipo_documento_prestacao_conta_relacao_bens.id,
                'nome': tipo_documento_prestacao_conta_relacao_bens.nome,
                'uuid': f'{tipo_documento_prestacao_conta_relacao_bens.uuid}'
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

