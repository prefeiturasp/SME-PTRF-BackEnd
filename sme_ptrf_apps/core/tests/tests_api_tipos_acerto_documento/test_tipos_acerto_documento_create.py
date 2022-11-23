import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoDocumento

pytestmark = pytest.mark.django_db


def test_create_tipo_acerto_documento(jwt_authenticated_client_a, tipo_documento_prestacao_conta_relacao_bens):
    payload_novo_tipo_acerto = {
        "nome": "tipo acerto documento teste",
        "categoria": TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS,
        "tipos_documento_prestacao": [tipo_documento_prestacao_conta_relacao_bens.id]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/tipos-acerto-documento/', data=json.dumps(payload_novo_tipo_acerto),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert TipoAcertoDocumento.objects.filter(uuid=result['uuid']).exists()


def test_create_tipo_acerto_documento_nome_igual(
    jwt_authenticated_client_a,
    tipo_acerto_documento_create,
    tipo_documento_prestacao_conta_relacao_bens
):
    payload_novo_tipo_acerto = {
        "nome": "Teste nome igual",
        "categoria": TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS,
        "tipos_documento_prestacao": [tipo_documento_prestacao_conta_relacao_bens.id]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/tipos-acerto-documento/', data=json.dumps(payload_novo_tipo_acerto),
        content_type='application/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'detail': 'Já existe um tipo de acerto de documento com esse nome.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(TipoAcertoDocumento.objects.filter(nome="Teste nome igual").all()) == 1
    assert resultado_esperado == result
