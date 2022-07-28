import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoLancamento

pytestmark = pytest.mark.django_db


def test_create_tipo_acerto_lancamento(jwt_authenticated_client_a):
    payload_novo_tipo_acerto = {
        "nome": "tipo acerto teste",
        "categoria": TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    }

    response = jwt_authenticated_client_a.post(
        f'/api/tipos-acerto-lancamento/', data=json.dumps(payload_novo_tipo_acerto),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert TipoAcertoLancamento.objects.filter(uuid=result['uuid']).exists()


def test_create_tipo_acerto_lancamento_nome_igual(jwt_authenticated_client_a, tipo_acerto_lancamento_create):
    payload_novo_tipo_acerto = {
        "nome": "Teste nome igual",
        "categoria": TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    }

    response = jwt_authenticated_client_a.post(
        f'/api/tipos-acerto-lancamento/', data=json.dumps(payload_novo_tipo_acerto),
        content_type='application/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'detail': 'Já existe um tipo de acerto de lançamento com esse nome.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(TipoAcertoLancamento.objects.filter(nome="Teste nome igual").all()) == 1
    assert resultado_esperado == result

