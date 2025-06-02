import pytest
from rest_framework import status
from ...models import AcaoPdde
from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from sme_ptrf_apps.paa.fixtures.factories import AcaoPddeFactory


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_acao_pdde(jwt_authenticated_client_sme, programa_pdde, flag_paa):

    for index in range(50):
        AcaoPddeFactory.create(nome=f"Ação-pdde-{index + 1}", programa=programa_pdde)

    response = jwt_authenticated_client_sme.get("/api/acoes-pdde/?programa_nome=Categ&nome=Ação")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 50
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]
    assert response.data["links"]['next'] is not None


@pytest.mark.django_db
def test_obtem_acao_pdde(jwt_authenticated_client_sme, acao_pdde, flag_paa):
    response = jwt_authenticated_client_sme.get(f"/api/acoes-pdde/{acao_pdde.uuid}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Ação PDDE Teste"


@pytest.mark.django_db
def test_cria_acao_pdde(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    data = {"nome": "Nova Ação", "programa": programa_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_201_CREATED
    assert AcaoPdde.objects.filter(nome="Nova Ação").exists()


@pytest.mark.django_db
def test_cria_acao_pdde_sem_nome(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    data = {"programa": programa_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'nome' in response.data
    assert response.data["nome"] == "Nome da ação PDDE não foi informado."


@pytest.mark.django_db
def test_cria_acao_pdde_sem_programa(jwt_authenticated_client_sme, flag_paa):
    data = {"nome": "novo"}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'programa' in response.data
    assert response.data["programa"] == "O Programa PDDE não foi informado."


@pytest.mark.django_db
def test_cria_acao_pdde_duplicado(jwt_authenticated_client_sme, acao_pdde, programa_pdde, flag_paa):
    data = {"nome": acao_pdde.nome, "programa": programa_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data["erro"] == "Duplicated"
    assert response.data["detail"] == ("Erro ao criar Ação PDDE. Já existe uma " +
                                       "Ação PDDE cadastrada com este nome e programa.")


@pytest.mark.django_db
def test_atualizar_acao_pdde_duplicado(jwt_authenticated_client_sme, acao_pdde, programa_pdde, flag_paa):
    cadastro = AcaoPddeFactory.create(nome="Novo", programa=programa_pdde)

    data = {"nome": acao_pdde.nome, "programa": programa_pdde.uuid}

    response = jwt_authenticated_client_sme.patch("/api/acoes-pdde/" + str(cadastro.uuid) + "/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data["erro"] == "Duplicated", response.content
    assert response.data["detail"] == ("Erro ao atualizar Ação PDDE. Já existe uma " +
                                       "Ação PDDE cadastrada com este nome e programa.")


@pytest.mark.django_db
def test_altera_acao_pdde(jwt_authenticated_client_sme, acao_pdde, flag_paa):
    data = {"nome": "Novo Nome", "programa": acao_pdde.programa.uuid}
    response = jwt_authenticated_client_sme.patch(f"/api/acoes-pdde/{acao_pdde.uuid}/", data)

    assert response.status_code == status.HTTP_200_OK, response.content
    acao_pdde.refresh_from_db()
    assert acao_pdde.nome == "Novo Nome"


@pytest.mark.django_db
def test_exclui_acao_pdde(jwt_authenticated_client_sme, flag_paa):
    acao = AcaoPddeFactory(nome="Deletar")
    response = jwt_authenticated_client_sme.delete(f"/api/acoes-pdde/{acao.uuid}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
