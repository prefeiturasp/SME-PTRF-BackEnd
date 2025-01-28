import json
import pytest
from unittest import mock

from django.db.models.deletion import ProtectedError
from rest_framework import status
from sme_ptrf_apps.despesas.models import TipoTransacao
from sme_ptrf_apps.despesas.api.views.tipos_transacao_viewset import TiposTransacaoViewSet

pytestmark = pytest.mark.django_db



def test_create(jwt_authenticated_client_d):

    payload = {
        'nome': 'Pix',
    }

    response = jwt_authenticated_client_d.post(
        f'/api/tipos-transacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert TipoTransacao.objects.filter(uuid=result['uuid']).exists()


def test_create_invalid_payload(jwt_authenticated_client_d):
    payload = {
        'nome2': 'Cheque',
    }

    response = jwt_authenticated_client_d.post(
        f'/api/tipos-transacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert TipoTransacao.objects.count() == 0


def test_create_erro_duplicado(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo1 = tipo_transacao_factory.create(nome="PIX")
    payload = {
        'nome': 'PIX',
    }

    response = jwt_authenticated_client_d.post(
        f'/api/tipos-transacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == {'non_field_errors': 'Este tipo de transação já existe.'}
    assert TipoTransacao.objects.count() == 1


def test_delete(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo_transacao = tipo_transacao_factory.create()
    assert TipoTransacao.objects.filter(uuid=tipo_transacao.uuid).exists()

    response = jwt_authenticated_client_d.delete(
        f'/api/tipos-transacao/{TipoTransacao.objects.first().uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not TipoTransacao.objects.filter(uuid=tipo_transacao.uuid).exists()


def test_delete_uuid_invalid(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo_transacao = tipo_transacao_factory.create()
    assert TipoTransacao.objects.filter(uuid=tipo_transacao.uuid).exists()

    response = jwt_authenticated_client_d.delete(
        f'/api/tipos-transacao/01829e9d-304b-47df-9725-234fe886600b/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert TipoTransacao.objects.filter(uuid=tipo_transacao.uuid).exists()


@mock.patch.object(TiposTransacaoViewSet, "perform_destroy")
def test_delete_exception(mock_perform_destroy, jwt_authenticated_client_d, tipo_transacao_factory):
    tipo_transacao = tipo_transacao_factory.create()
    mock_perform_destroy.side_effect = ProtectedError("Erro", TipoTransacao)
    assert TipoTransacao.objects.filter(uuid=tipo_transacao.uuid).exists()
    
    response = jwt_authenticated_client_d.delete(
        f'/api/tipos-transacao/{tipo_transacao.uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert TipoTransacao.objects.filter(uuid=tipo_transacao.uuid).exists()


def test_get(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo_transacao = tipo_transacao_factory.create()
    response = jwt_authenticated_client_d.get(
        f'/api/tipos-transacao/{tipo_transacao.uuid}/',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        'nome': tipo_transacao.nome,
        'id': tipo_transacao.id,
        'tem_documento': False,
        'uuid': str(tipo_transacao.uuid)
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_get_invalid_uuid(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo_transacao_factory.create()
    response = jwt_authenticated_client_d.get(
        f'/api/tipos-transacao/01829e9d-304b-47df-9725-234fe886600b/',
        content_type='applicaton/json'
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_filtra_nome(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo1 = tipo_transacao_factory.create(nome="PIX")
    tipo2 = tipo_transacao_factory.create(nome="TED")
    response = jwt_authenticated_client_d.get(f'/api/tipos-transacao/?nome=PIX', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'nome': tipo1.nome,
            'id': tipo1.id,
            'tem_documento': False,
            'uuid': str(tipo1.uuid)
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_update(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo1 = tipo_transacao_factory.create(nome="PIX")
    payload = {
        'nome': 'PIX2',
    }

    response = jwt_authenticated_client_d.patch(
        f'/api/tipos-transacao/{tipo1.uuid}/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert TipoTransacao.objects.filter(uuid=tipo1.uuid).first().nome == "PIX2"


def test_update_erro_duplicado(jwt_authenticated_client_d, tipo_transacao_factory):
    tipo1 = tipo_transacao_factory.create(nome="PIX")
    tipo2 = tipo_transacao_factory.create(nome="TED")
    payload = {
        'nome': 'TED',
    }

    response = jwt_authenticated_client_d.patch(
        f'/api/tipos-transacao/{tipo1.uuid}/', data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == {'non_field_errors': 'Este tipo de transação já existe.'}
    assert TipoTransacao.objects.filter(uuid=tipo1.uuid).first().nome == "PIX"