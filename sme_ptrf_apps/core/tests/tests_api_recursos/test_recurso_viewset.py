import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from ...api.views.recursos_viewset import RecursoViewSet
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('premio-excelencia', active=True)
def test_list_recursos(recurso_factory, usuario_permissao_associacao):
    """Teste list retorna 200 OK e lista de recursos"""
    recurso_factory.create(nome='Recurso A', ativo=True)
    recurso_factory.create(nome='Recurso B', ativo=True)

    request = APIRequestFactory().get("/api/recursos")
    view = RecursoViewSet.as_view({'get': 'list'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@override_flag('premio-excelencia', active=True)
def test_retrieve_recurso(recurso, usuario_permissao_associacao):
    """Teste retrieve retorna 200 OK com dados corretos"""
    request = APIRequestFactory().get("")
    view = RecursoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request, uuid=recurso.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(recurso.uuid)
    assert response.data['nome'] == recurso.nome
    assert response.data['nome_exibicao'] == recurso.nome_exibicao


@override_flag('premio-excelencia', active=True)
@pytest.mark.django_db(transaction=True)
def test_retrieve_invalid_uuid(usuario_permissao_associacao):
    """Teste retrieve com UUID inválido retorna 404"""
    from uuid import uuid4
    request = APIRequestFactory().get("")
    view = RecursoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request, uuid=uuid4())

    assert response.status_code == status.HTTP_404_NOT_FOUND


@override_flag('premio-excelencia', active=True)
def test_recursos_disponiveis_action(recurso, usuario_permissao_associacao):
    """Teste action recursos_disponiveis retorna 200 OK"""
    request = APIRequestFactory().get("")
    view = RecursoViewSet.as_view({'get': 'recursos_disponiveis'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)


@override_flag('premio-excelencia', active=True)
def test_list_ordena_por_nome(recurso_factory, usuario_permissao_associacao):
    """Teste que list ordena por nome alfabeticamente"""
    recurso_factory.create(nome='Zebra', ativo=True)
    recurso_factory.create(nome='Apple', ativo=True)
    recurso_factory.create(nome='Banana', ativo=True)

    request = APIRequestFactory().get("")
    view = RecursoViewSet.as_view({'get': 'list'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    nomes = [r['nome'] for r in response.data]
    assert nomes == sorted(nomes)


@override_flag('premio-excelencia', active=True)
def test_list_filtra_apenas_ativos(recurso_factory, usuario_permissao_associacao):
    """Teste que queryset filtra apenas recursos ativos"""
    recurso_factory.create(nome='Ativo', ativo=True)
    recurso_factory.create(nome='Inativo', ativo=False)

    request = APIRequestFactory().get("")
    view = RecursoViewSet.as_view({'get': 'list'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nome'] == 'Ativo'


def test_viewset_usa_uuid_como_lookup_field(recurso, usuario_permissao_associacao):
    """Teste que viewset usa uuid como lookup_field"""
    viewset = RecursoViewSet()
    assert viewset.lookup_field == 'uuid'


def test_viewset_requer_autenticacao():
    """Teste que viewset requer autenticação"""
    viewset = RecursoViewSet()
    from rest_framework.permissions import IsAuthenticated
    assert IsAuthenticated in viewset.permission_classes


def test_viewset_serializer_class():
    """Teste que viewset usa RecursoSerializer"""
    from sme_ptrf_apps.core.api.serializers.recurso_serializer import RecursoSerializer
    viewset = RecursoViewSet()
    assert viewset.serializer_class == RecursoSerializer