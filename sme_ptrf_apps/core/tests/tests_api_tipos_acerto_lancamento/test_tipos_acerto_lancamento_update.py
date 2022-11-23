import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoLancamento

pytestmark = pytest.mark.django_db


def test_update_tipo_acerto_lancamento(jwt_authenticated_client_a, tipo_acerto_lancamento_update):
    assert TipoAcertoLancamento.objects.get(uuid=tipo_acerto_lancamento_update.uuid).nome == 'Teste update'

    payload = {
        'nome': 'Teste update funcionando',
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/tipos-acerto-lancamento/{tipo_acerto_lancamento_update.uuid}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert TipoAcertoLancamento.objects.get(uuid=tipo_acerto_lancamento_update.uuid).nome == payload['nome']


def test_update_tipo_acerto_lancamento_nome_igual(
    jwt_authenticated_client_a,
    tipo_acerto_lancamento_update,
    tipo_acerto_lancamento_update_nome_igual
):
    payload_novo_tipo_acerto = {
        "nome": "Teste nome igual update",
        "categoria": TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/tipos-acerto-lancamento/{tipo_acerto_lancamento_update.uuid}/',
        data=json.dumps(payload_novo_tipo_acerto), content_type='application/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'detail': 'Já existe um tipo de acerto de lançamento com esse nome.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(TipoAcertoLancamento.objects.filter(nome="Teste nome igual update").all()) == 1
    assert resultado_esperado == result

