import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoLancamento

pytestmark = pytest.mark.django_db


def test_create_tipo_acerto_lancamento(jwt_authenticated_client_a, recurso_legado):
    payload_novo_tipo_acerto = {
        "nome": "tipo acerto teste",
        "categoria": TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO,
        "pode_alterar_saldo_conciliacao": False,
        "recurso": str(recurso_legado.uuid),
    }

    response = jwt_authenticated_client_a.post(
        '/api/tipos-acerto-lancamento/', data=json.dumps(payload_novo_tipo_acerto),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert TipoAcertoLancamento.objects.filter(uuid=result['uuid']).exists()
    assert result['pode_alterar_saldo_conciliacao'] == payload_novo_tipo_acerto['pode_alterar_saldo_conciliacao']
    assert result['recurso'] == payload_novo_tipo_acerto['recurso']


def test_create_tipo_acerto_lancamento_nome_igual(
    jwt_authenticated_client_a,
    tipo_acerto_lancamento_create,
    recurso_legado
):
    payload_novo_tipo_acerto = {
        "nome": "Teste nome igual",
        "categoria": TipoAcertoLancamento.CATEGORIA_DEVOLUCAO,
        "recurso": str(recurso_legado.uuid),
    }

    response = jwt_authenticated_client_a.post(
        '/api/tipos-acerto-lancamento/', data=json.dumps(payload_novo_tipo_acerto),
        content_type='application/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'detail': 'Já existe um tipo de acerto de lançamento com esse nome e categoria para esse recurso.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(TipoAcertoLancamento.objects.filter(nome="Teste nome igual").all()) == 1
    assert resultado_esperado == result
