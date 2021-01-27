import json

import pytest
from model_bakery import baker
from rest_framework import status

from ...models import Despesa

pytestmark = pytest.mark.django_db


@pytest.fixture
def acao_e_recurso_proprio():
    return baker.make('Acao', nome='PTRF-Recurso-Proprio', e_recursos_proprios=True)


@pytest.fixture
def acao_associacao_e_recurso_proprio(associacao, acao_e_recurso_proprio):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_e_recurso_proprio
    )


@pytest.fixture
def payload_despesa_recurso_proprio(
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao_e_recurso_proprio,
    tipo_aplicacao_recurso,
    tipo_custeio,
    especificacao_material_servico
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "tipo_documento": tipo_documento.id,
        "data_documento": "2020-03-10",
        "numero_documento": "634767",
        "tipo_transacao": tipo_transacao.id,
        "data_transacao": "2020-03-10",
        "valor_total": 11000.50, # "valor_realizado"
        "valor_original": 11000.50, # "valor documento"
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao_e_recurso_proprio.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 11000.50,
                "valor_original": 11000.50
            }
        ]
    }

    return payload


def test_cadastrar_despesa_recurso_proprio(jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao_e_recurso_proprio,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_recurso_proprio):
    from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO

    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_recurso_proprio), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid
    assert despesa.status == STATUS_COMPLETO

