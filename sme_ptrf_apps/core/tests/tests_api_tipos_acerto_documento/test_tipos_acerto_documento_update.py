import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoDocumento

pytestmark = pytest.mark.django_db


def test_update_tipo_acerto_documento(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01
):
    assert TipoAcertoDocumento.objects.get(uuid=tipo_acerto_documento_01.uuid).nome == 'teste'

    payload = {
        'nome': 'Teste update funcionando',
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/tipos-acerto-documento/{tipo_acerto_documento_01.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert TipoAcertoDocumento.objects.get(uuid=tipo_acerto_documento_01.uuid).nome == payload['nome']


def test_update_tipo_acerto_documento_nome_igual(
    jwt_authenticated_client_a,
    tipo_acerto_documento_01,
    tipo_acerto_documento_create
):
    payload_novo_tipo_acerto = {
        "nome": "Teste nome igual",
        "categoria": TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/tipos-acerto-documento/{tipo_acerto_documento_01.uuid}/',
        data=json.dumps(payload_novo_tipo_acerto), content_type='application/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'detail': 'Já existe um tipo de acerto de documento com esse nome.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(TipoAcertoDocumento.objects.filter(nome="Teste nome igual").all()) == 1
    assert resultado_esperado == result

