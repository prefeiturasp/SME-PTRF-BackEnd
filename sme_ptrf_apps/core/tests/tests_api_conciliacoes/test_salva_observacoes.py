import json

import pytest
from rest_framework import status

from ...models import ObservacaoConciliacao

pytestmark = pytest.mark.django_db


def test_api_salva_observacoes_conciliacao(jwt_authenticated_client_a, periodo, conta_associacao_cartao, acao_associacao_ptrf):
    url = f'/api/conciliacoes/salvar-observacoes/'

    observacao = "Teste observações."
    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "observacoes": [{
            "acao_associacao_uuid": f'{acao_associacao_ptrf.uuid}',
            "observacao": observacao
        }]
    }

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert ObservacaoConciliacao.objects.exists()


def test_api_salva_observacoes_conciliacao_vazia(jwt_authenticated_client_a, periodo, conta_associacao_cartao, acao_associacao_ptrf):
    url = f'/api/conciliacoes/salvar-observacoes/'

    observacao = ""
    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "observacoes": [{
            "acao_associacao_uuid": f'{acao_associacao_ptrf.uuid}',
            "observacao": observacao
        }]
    }

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert not ObservacaoConciliacao.objects.exists()
