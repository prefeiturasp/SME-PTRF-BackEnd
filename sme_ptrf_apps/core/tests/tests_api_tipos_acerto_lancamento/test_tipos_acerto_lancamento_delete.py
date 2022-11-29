import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoLancamento

import json

pytestmark = pytest.mark.django_db


def test_delete_tipo_acerto_lancamento(jwt_authenticated_client_a, tipo_acerto_lancamento_delete):
    assert TipoAcertoLancamento.objects.filter(uuid=tipo_acerto_lancamento_delete.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/tipos-acerto-lancamento/{tipo_acerto_lancamento_delete.uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not TipoAcertoLancamento.objects.filter(uuid=tipo_acerto_lancamento_delete.uuid).exists()


def test_delete_tipo_acerto_lancamento_sendo_utilizado(
    jwt_authenticated_client_a,
    tipo_acerto_lancamento_delete_02,
    solicitacao_acerto_lancamento_delete
):
    assert TipoAcertoLancamento.objects.filter(uuid=tipo_acerto_lancamento_delete_02.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/tipos-acerto-lancamento/{tipo_acerto_lancamento_delete_02.uuid}/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'ProtectedError',
        'mensagem': 'Esse tipo de lançamento não pode ser excluído pois existem solicitações de acertos com ele'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert resultado_esperado == result
    assert TipoAcertoLancamento.objects.filter(uuid=tipo_acerto_lancamento_delete_02.uuid).exists()



