import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_endpoint_lista_valores_reprogramados(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao
):
    response = jwt_authenticated_client_a.get(
        f'/api/valores-reprogramados/get-valores-reprogramados/?associacao_uuid={associacao.uuid}')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_status_valores_reprogramados(
    jwt_authenticated_client_a,
    associacao,
):
    response = jwt_authenticated_client_a.get(
        f'/api/valores-reprogramados/get-status-valores-reprogramados/?associacao_uuid={associacao.uuid}')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_salvar_valor_reprogramado(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):

    payload = {
        "associacao_uuid": f"{associacao.uuid}",
        "dadosForm": {
            "associacao": {
                "status_valores_reprogramados": associacao.status_valores_reprogramados,
                "uuid": f"{associacao.uuid}"
            },
            "contas": [{
                "conta": {
                    "acoes": [{
                        "custeio": {
                            "nome": "custeio",
                            "status_conferencia": None,
                            "valor_dre": None,
                            "valor_ue": None
                        },
                        "nome": acao_associacao.acao.nome,
                        "uuid": f"{acao_associacao.uuid}"
                    }],
                    "tipo_conta": conta_associacao.tipo_conta.nome,
                    "uuid": f"{conta_associacao.uuid}"
                }
            }]
        },
        "visao": "UE"
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/valores-reprogramados/salvar-valores-reprogramados/', data=json.dumps(payload),
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED


def test_endpoint_concluir_valor_reprogramado(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):

    payload = {
        "associacao_uuid": f"{associacao.uuid}",
        "dadosForm": {
            "associacao": {
                "status_valores_reprogramados": associacao.status_valores_reprogramados,
                "uuid": f"{associacao.uuid}"
            },
            "contas": [{
                "conta": {
                    "acoes": [{
                        "custeio": {
                            "nome": "custeio",
                            "status_conferencia": None,
                            "valor_dre": 0.10,
                            "valor_ue": 0.20
                        },
                        "nome": acao_associacao.acao.nome,
                        "uuid": f"{acao_associacao.uuid}"
                    }],
                    "tipo_conta": conta_associacao.tipo_conta.nome,
                    "uuid": f"{conta_associacao.uuid}"
                }
            }]
        },
        "visao": "DRE"
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/valores-reprogramados/concluir-valores-reprogramados/', data=json.dumps(payload),
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED

