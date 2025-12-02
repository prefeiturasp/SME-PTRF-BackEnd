import pytest
from django.urls import reverse
from rest_framework import status
from ...models import OutroRecurso
from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoFactory

BASE_URL = reverse("api:outros-recursos-paa-list")


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_outros_recursos(jwt_authenticated_client_sme, flag_paa):
    for index in range(50):
        OutroRecursoFactory.create(nome=f"Outro-Recurso-{index + 1}")

    response = jwt_authenticated_client_sme.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 50
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]
    assert response.data["links"]['next'] is not None


@pytest.mark.django_db
def test_obtem_outro_recurso(jwt_authenticated_client_sme, outros_recursos, flag_paa):
    url = reverse("api:outros-recursos-paa-detail", args=[outros_recursos.uuid])
    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == outros_recursos.nome


@pytest.mark.django_db
def test_cria_outros_recursos(jwt_authenticated_client_sme, flag_paa):
    data = {"nome": "Novo Recurso"}
    response = jwt_authenticated_client_sme.post(BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert OutroRecurso.objects.filter(nome=data.get('nome')).exists()


@pytest.mark.django_db
def test_cria_outros_recursos_sem_nome(jwt_authenticated_client_sme, flag_paa):
    data = {"nome": ""}
    response = jwt_authenticated_client_sme.post(BASE_URL, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'nome' in result
    assert result["nome"] == ["Nome do Recurso não foi informado."]


@pytest.mark.django_db
def test_cria_outros_recursos_duplicado(jwt_authenticated_client_sme, outros_recursos, flag_paa):
    data = {"nome": outros_recursos.nome}
    response = jwt_authenticated_client_sme.post(BASE_URL, data)
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in result
    assert result["non_field_errors"] == ["Já existe um Recurso cadastrado com esse nome."]


@pytest.mark.django_db
def test_atualizar_outros_recursos_duplicado(jwt_authenticated_client_sme, outros_recursos, flag_paa):
    cadastrado = OutroRecursoFactory(nome="Teste")
    data = {"nome": cadastrado.nome}
    url = reverse("api:outros-recursos-paa-detail", args=[outros_recursos.uuid])

    response = jwt_authenticated_client_sme.patch(url, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in result
    assert result["non_field_errors"] == ["Já existe um Recurso cadastrado com esse nome."]


@pytest.mark.django_db
def test_altera_outros_recursos(jwt_authenticated_client_sme, outros_recursos, flag_paa):
    data = {"nome": "Novo Nome"}
    url = reverse("api:outros-recursos-paa-detail", args=[outros_recursos.uuid])
    response = jwt_authenticated_client_sme.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    outros_recursos.refresh_from_db()
    assert outros_recursos.nome == "Novo Nome"


@pytest.mark.django_db
def test_exclui_outros_recursos(jwt_authenticated_client_sme, flag_paa):
    remover = OutroRecursoFactory(nome="Deletar")
    url = reverse("api:outros-recursos-paa-detail", args=[remover.uuid])
    response = jwt_authenticated_client_sme.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not OutroRecurso.objects.filter(uuid=remover.uuid).exists()


@pytest.mark.django_db
def test_exclui_outros_recursos_inexistente(jwt_authenticated_client_sme, flag_paa):
    """Testa a exclusão de um recurso que não existe"""
    from uuid import uuid4
    uuid_inexistente = uuid4()
    url = reverse("api:outros-recursos-paa-detail", args=[uuid_inexistente])
    response = jwt_authenticated_client_sme.delete(url)
    result = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Recurso não encontrado." in result["detail"]
