import json

import pytest
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import Observacao, PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_salva_prestacao_conta(client, prestacao_conta_iniciada, acao_associacao_ptrf):
    url = f'/api/prestacoes-contas/{prestacao_conta_iniciada.uuid}/salvar/'

    observacao = "Teste observações."
    payload = {
        "observacoes": [{
            "acao_associacao_uuid": str(acao_associacao_ptrf.uuid),
            "observacao": observacao
        }]
    }

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    prestacao_salva = PrestacaoConta.by_uuid(uuid=prestacao_conta_iniciada.uuid)
    result_esperado = PrestacaoContaLookUpSerializer(
        prestacao_salva,
        many=False).data

    # Converto os campos UUIDs em strings para que a comparação funcione
    result_esperado['conta_associacao_uuid'] = f'{result_esperado["conta_associacao_uuid"]}'
    result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a prestação de contas esperada."

    assert not prestacao_salva.conciliado, "Flag conciliado deve continuar falso."
    assert prestacao_salva.conciliado_em == None, "Não deveria haver data da última conciliação."

    assert Observacao.objects.filter(prestacao_conta__uuid=prestacao_conta_iniciada.uuid,
                                     acao_associacao__uuid=acao_associacao_ptrf.uuid).exists()


def test_api_salva_prestacao_conta_sem_observacoes(client, prestacao_conta_iniciada, acao_associacao_ptrf):
    url = f'/api/prestacoes-contas/{prestacao_conta_iniciada.uuid}/salvar/'

    payload = {
        "observacoes": [{
            "acao_associacao_uuid": str(acao_associacao_ptrf.uuid),
            "observacao": ''
        }]
    }

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK, "Deve aceitar o campo observacoes vazio."
    assert not Observacao.objects.filter(prestacao_conta__uuid=prestacao_conta_iniciada.uuid,
                                         acao_associacao__uuid=acao_associacao_ptrf.uuid).exists()


def test_api_salva_prestacao_conta_sem_payload(client, prestacao_conta_iniciada):
    url = f'/api/prestacoes-contas/{prestacao_conta_iniciada.uuid}/salvar/'

    response = client.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK, "Deve aceitar o campo observacoes vazio."
