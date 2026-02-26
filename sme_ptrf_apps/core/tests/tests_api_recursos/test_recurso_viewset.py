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
    assert len(response.data) == 3


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
def test_list_recursos_por_unidade(jwt_authenticated_client_a, recurso, unidade, associacao, periodo_inicial_associacao_factory):
    periodo_inicial_associacao_factory(
        associacao=associacao,
        recurso=recurso
    )

    response = jwt_authenticated_client_a.get(
        '/api/recursos/por-unidade/',
        {'uuid_unidade': unidade.uuid},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@override_flag('premio-excelencia', active=True)
def test_list_recursos_por_unidade_sem_periodo_inicial(jwt_authenticated_client_a, unidade):

    response = jwt_authenticated_client_a.get(
        '/api/recursos/por-unidade/',
        {'uuid_unidade': unidade.uuid},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
