import pytest
from rest_framework import status
from ...models import CategoriaPdde
from sme_ptrf_apps.core.fixtures.factories import CategoriaPddeFactory, FlagFactory


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_categoria(jwt_authenticated_client_sme, flag_paa):
    CategoriaPddeFactory(nome="Categoria-teste-1")
    CategoriaPddeFactory(nome="Categoria-teste-2")
    CategoriaPddeFactory(nome="Categoria-teste-3")
    CategoriaPddeFactory(nome="Categoria-teste-4")

    response = jwt_authenticated_client_sme.get("/api/categorias-pdde/?nome=Categoria-teste")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 4
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]


@pytest.mark.django_db
def test_obtem_categoria(jwt_authenticated_client_sme, categoria_pdde, flag_paa):
    response = jwt_authenticated_client_sme.get(f"/api/categorias-pdde/{categoria_pdde.uuid}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Categoria PDDE Teste"


@pytest.mark.django_db
def test_cria_categoria(jwt_authenticated_client_sme, flag_paa):
    data = {"nome": "Nova Categoria"}
    response = jwt_authenticated_client_sme.post("/api/categorias-pdde/", data)

    assert response.status_code == status.HTTP_201_CREATED
    assert CategoriaPdde.objects.filter(nome="Nova Categoria").exists()


@pytest.mark.django_db
def test_cria_categoria_sem_nome(jwt_authenticated_client_sme, flag_paa):
    data = {}
    response = jwt_authenticated_client_sme.post("/api/categorias-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'nome' in response.data
    assert response.data["nome"] == "Nome da Categoria PDDE não foi informado."


@pytest.mark.django_db
def test_cria_categoria_duplicada(jwt_authenticated_client_sme, categoria_pdde, flag_paa):
    data = {"nome": categoria_pdde.nome}
    response = jwt_authenticated_client_sme.post("/api/categorias-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data["erro"] == "Duplicated"
    assert response.data["detail"] == ("Erro ao criar Categoria PDDE. Já existe uma "
                                       "Categoria PDDE cadastrada com este nome.")


@pytest.mark.django_db
def test_altera_categoria(jwt_authenticated_client_sme, categoria_pdde, flag_paa):
    data = {"nome": "Novo Nome"}
    response = jwt_authenticated_client_sme.patch(f"/api/categorias-pdde/{categoria_pdde.uuid}/", data)

    assert response.status_code == status.HTTP_200_OK
    categoria_pdde.refresh_from_db()
    assert categoria_pdde.nome == "Novo Nome"


@pytest.mark.django_db
def test_altera_categoria_para_duplicado_existente(jwt_authenticated_client_sme, categoria_pdde, flag_paa):
    categoria = CategoriaPddeFactory(nome="Novo Nome")
    data = {"nome": categoria_pdde.nome}
    response = jwt_authenticated_client_sme.patch(f"/api/categorias-pdde/{categoria.uuid}/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data['erro'] == 'Duplicated'
    assert response.data['detail'] == ("Erro ao atualizar Categoria PDDE. Já existe uma " +
                                       "Categoria PDDE cadastrada com este nome.")


@pytest.mark.django_db
def test_exclui_categoria(jwt_authenticated_client_sme, categoria_pdde, flag_paa):
    response = jwt_authenticated_client_sme.delete(f"/api/categorias-pdde/{categoria_pdde.uuid}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not CategoriaPdde.objects.filter(uuid=categoria_pdde.uuid).exists()


@pytest.mark.django_db
def test_exclui_categoria_vinculado(jwt_authenticated_client_sme, acao_pdde, flag_paa):
    response = jwt_authenticated_client_sme.delete(f"/api/categorias-pdde/{acao_pdde.categoria.uuid}/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["erro"] == "ProtectedError"
    assert response.data == {
        'erro': 'ProtectedError',
        'mensagem': 'Essa operação não pode ser realizada. Há Ações PDDE vinculadas a esta categoria.'
    }
