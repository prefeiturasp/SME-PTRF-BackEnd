import pytest
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from sme_ptrf_apps.core.models import Recurso
from ...api.views.acoes_viewset import AcoesViewSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def acao_x(acao_factory):
    return acao_factory.create(nome='X')


@pytest.fixture
def recurso_nao_legado():
    recurso, _ = Recurso.objects.get_or_create(
        nome="Recurso Não Legado",
        defaults={
            "nome_exibicao": "Não Legado",
            "cor": "#000000",
            "legado": False,
        },
    )
    return recurso


@pytest.fixture
def acao_com_recurso_legado(acao_factory):
    return acao_factory.create(nome='Acao Legado')


@pytest.fixture
def acao_sem_recurso_legado(acao_factory, recurso_nao_legado):
    return acao_factory.create(nome='Acao Nao Legado', recurso=recurso_nao_legado)


def test_view_set(acao_x, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AcoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_acoes_ptrf_retorna_apenas_acoes_com_recurso_legado(
    acao_com_recurso_legado, acao_sem_recurso_legado, usuario_permissao_associacao
):
    request = APIRequestFactory().get("")
    view = AcoesViewSet.as_view({'get': 'acoes_ptrf'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    uuids_retornados = [str(a['uuid']) for a in response.data]
    assert str(acao_com_recurso_legado.uuid) in uuids_retornados
    assert str(acao_sem_recurso_legado.uuid) not in uuids_retornados


def test_acoes_ptrf_retorna_lista_vazia_sem_acoes_legado(
    acao_sem_recurso_legado, usuario_permissao_associacao
):
    request = APIRequestFactory().get("")
    view = AcoesViewSet.as_view({'get': 'acoes_ptrf'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_acoes_ptrf_nao_autenticado_retorna_401():
    request = APIRequestFactory().get("")
    view = AcoesViewSet.as_view({'get': 'acoes_ptrf'})
    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_retorna_200(acao_x, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    view = AcoesViewSet.as_view({'get': 'list'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    uuids = [str(a['uuid']) for a in response.data]
    assert str(acao_x.uuid) in uuids


def test_list_com_filtro_nome(acao_x, acao_com_recurso_legado, usuario_permissao_associacao):
    request = APIRequestFactory().get("", {'nome': 'X'})
    view = AcoesViewSet.as_view({'get': 'list'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    uuids = [str(a['uuid']) for a in response.data]
    assert str(acao_x.uuid) in uuids
    assert str(acao_com_recurso_legado.uuid) not in uuids


def test_list_nao_autenticado_retorna_401():
    request = APIRequestFactory().get("")
    view = AcoesViewSet.as_view({'get': 'list'})
    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_retrieve_nao_autenticado_retorna_401(acao_x):
    request = APIRequestFactory().get("")
    view = AcoesViewSet.as_view({'get': 'retrieve'})
    response = view(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_retorna_201(usuario_permissao_associacao):
    recurso = Recurso.objects.get(legado=True)
    payload = {
        'nome': 'Nova Acao Teste',
        'recurso': str(recurso.uuid),
        'aceita_capital': True,
        'aceita_custeio': False,
        'aceita_livre': False,
        'e_recursos_proprios': False,
        'posicao_nas_pesquisas': 'AAAA',
        'exibir_paa': True,
    }
    request = APIRequestFactory().post("", payload, format='json')
    view = AcoesViewSet.as_view({'post': 'create'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['nome'] == 'Nova Acao Teste'
    assert response.data['aceita_capital'] is True


def test_create_nao_autenticado_retorna_401():
    recurso = Recurso.objects.get(legado=True)
    payload = {'nome': 'Nova Acao', 'recurso': str(recurso.uuid)}
    request = APIRequestFactory().post("", payload, format='json')
    view = AcoesViewSet.as_view({'post': 'create'})
    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_retorna_200(acao_x, usuario_permissao_associacao):
    recurso = Recurso.objects.get(legado=True)
    payload = {
        'nome': 'X Atualizado',
        'recurso': str(recurso.uuid),
        'aceita_capital': True,
        'aceita_custeio': True,
        'aceita_livre': False,
        'e_recursos_proprios': False,
        'posicao_nas_pesquisas': 'BBBB',
        'exibir_paa': True,
    }
    request = APIRequestFactory().put("", payload, format='json')
    view = AcoesViewSet.as_view({'put': 'update'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'X Atualizado'
    assert response.data['aceita_capital'] is True


def test_partial_update_retorna_200(acao_x, usuario_permissao_associacao):
    payload = {'aceita_custeio': True}
    request = APIRequestFactory().patch("", payload, format='json')
    view = AcoesViewSet.as_view({'patch': 'partial_update'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['aceita_custeio'] is True


def test_destroy_retorna_204(acao_x, usuario_permissao_associacao):
    request = APIRequestFactory().delete("")
    view = AcoesViewSet.as_view({'delete': 'destroy'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_destroy_retorna_400_quando_protected_error(acao_x, usuario_permissao_associacao):
    from django.db.models.deletion import ProtectedError

    request = APIRequestFactory().delete("")
    view = AcoesViewSet.as_view({'delete': 'destroy'})
    force_authenticate(request, user=usuario_permissao_associacao)

    with patch.object(AcoesViewSet, 'perform_destroy', side_effect=ProtectedError("protected", set())):
        response = view(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'ProtectedError'


def test_destroy_nao_autenticado_retorna_401(acao_x):
    request = APIRequestFactory().delete("")
    view = AcoesViewSet.as_view({'delete': 'destroy'})
    response = view(request, uuid=acao_x.uuid)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
