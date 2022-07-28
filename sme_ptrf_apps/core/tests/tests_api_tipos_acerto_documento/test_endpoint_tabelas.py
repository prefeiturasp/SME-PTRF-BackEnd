import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoDocumento, TipoDocumentoPrestacaoConta
from sme_ptrf_apps.utils.choices_to_json import choices_to_json

pytestmark = pytest.mark.django_db


def test_api_list_categorias(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-documento/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    assert result["categorias"] == choices_to_json(TipoAcertoDocumento.CATEGORIA_CHOICES)
    assert response.status_code == status.HTTP_200_OK


def test_api_list_tipos_documentos(jwt_authenticated_client_a, tipo_documento_prestacao_conta_relacao_bens):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-documento/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    assert result["documentos"] == [
        {'id': tipo_documento_prestacao_conta_relacao_bens.id, 'nome': 'Relação de bens da conta'}
    ]
    assert response.status_code == status.HTTP_200_OK

