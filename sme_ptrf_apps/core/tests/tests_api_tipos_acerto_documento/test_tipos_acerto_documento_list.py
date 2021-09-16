import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_documento_prestacao_conta_ata():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas')


@pytest.fixture
def tipo_documento_prestacao_conta_relacao_bens():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Relação de bens da conta')


@pytest.fixture
def tipo_acerto_documento_assinatura(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar com assinatura')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_enviar(tipo_documento_prestacao_conta_ata, tipo_documento_prestacao_conta_relacao_bens):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar o documento')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_relacao_bens)
    tipo_acerto.save()
    return tipo_acerto


def test_api_list_tipos_acerto_documento_todos(
    jwt_authenticated_client_a,
    tipo_acerto_documento_assinatura,
    tipo_acerto_documento_enviar
):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-documento/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_acerto_documento_assinatura.id,
            'nome': 'Enviar com assinatura',
            'uuid': f'{tipo_acerto_documento_assinatura.uuid}'
        },
        {
            'id': tipo_acerto_documento_enviar.id,
            'nome': 'Enviar o documento',
            'uuid': f'{tipo_acerto_documento_enviar.uuid}'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_tipos_acerto_documento_por_tipo_documento(
    jwt_authenticated_client_a,
    tipo_acerto_documento_assinatura,
    tipo_acerto_documento_enviar,
    tipo_documento_prestacao_conta_relacao_bens,
    tipo_documento_prestacao_conta_ata
):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-documento/?tipos_documento_prestacao__uuid={tipo_documento_prestacao_conta_relacao_bens.uuid}', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_acerto_documento_enviar.id,
            'nome': 'Enviar o documento',
            'uuid': f'{tipo_acerto_documento_enviar.uuid}'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
