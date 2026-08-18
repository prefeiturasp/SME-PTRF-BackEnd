import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import FiqueDeOlho, TipoTextoFiqueDeOlhoChoices

pytestmark = pytest.mark.django_db


def test_create_fique_de_olho(jwt_authenticated_client_a, recurso_legado):

    payload = {
        'texto': "Fique de Olho Novo",
        'tipo_texto': TipoTextoFiqueDeOlhoChoices.ASSOCIACOES_PRESTACAO_CONTAS.value,
        'recurso': f'{recurso_legado.uuid}'
    }

    response = jwt_authenticated_client_a.post(
        '/api/fique-de-olho/', data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert FiqueDeOlho.objects.filter(uuid=result['uuid']).exists()


def test_create_fique_de_olho_tipo_texto_e_recurso_ja_existente(jwt_authenticated_client_a, fique_de_olho_a):
    payload = {
        'texto': 'Fique de Olho Novo',
        'tipo_texto': fique_de_olho_a.tipo_texto,
        'recurso': f'{fique_de_olho_a.recurso.uuid}'
    }

    response = jwt_authenticated_client_a.post(
        '/api/fique-de-olho/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    assert result == {"non_field_errors": [
        "Já existe um registro para este tipo de texto e recurso."
    ]}
