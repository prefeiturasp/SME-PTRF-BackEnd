import pytest
from django.urls import reverse

from rest_framework import status
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices, ObjetivoPaa


@pytest.mark.django_db
def test_list_default_objetivo_paa(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get("/api/objetivos-paa/")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 0
    assert 'count' in result
    assert result['count'] == 0
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_objetivos_paa(
        jwt_authenticated_client_sme, flag_paa, objetivo_paa_ativo, objetivo_paa_inativo, objetivo_paa_sem_paa):

    response = jwt_authenticated_client_sme.get("/api/objetivos-paa/")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 3
    assert 'count' in result
    assert result['count'] == 3
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_objetivos_paa_filtro_ativo(
        jwt_authenticated_client_sme, flag_paa, objetivo_paa_ativo, objetivo_paa_inativo, objetivo_paa_sem_paa):

    response = jwt_authenticated_client_sme.get("/api/objetivos-paa/?status=1")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 2
    assert 'count' in result
    assert result['count'] == 2
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_objetivos_paa_filtro_inativo(
        jwt_authenticated_client_sme, flag_paa, objetivo_paa_ativo, objetivo_paa_inativo, objetivo_paa_sem_paa):

    response = jwt_authenticated_client_sme.get("/api/objetivos-paa/?status=0")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 1
    assert 'count' in result
    assert result['count'] == 1
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_objetivos_paa_filtro_nome_exact(
        jwt_authenticated_client_sme, flag_paa, objetivo_paa_ativo, objetivo_paa_inativo, objetivo_paa_sem_paa):

    response = jwt_authenticated_client_sme.get(f"/api/objetivos-paa/?nome={objetivo_paa_ativo.nome}")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 1
    assert 'count' in result
    assert result['count'] == 1
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_objetivos_paa_filtro_nome_icontains(
        jwt_authenticated_client_sme, flag_paa, objetivo_paa_ativo, objetivo_paa_inativo, objetivo_paa_sem_paa):

    response = jwt_authenticated_client_sme.get(f"/api/objetivos-paa/?nome={objetivo_paa_ativo.nome[:-2]}")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 3
    assert 'count' in result
    assert result['count'] == 3
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_tabelas_endpoint(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get("/api/objetivos-paa/tabelas/")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert result['status'] == StatusChoices.to_dict()


@pytest.mark.django_db
def test_cria_objetivo_paa_sem_nome(jwt_authenticated_client_sme, flag_paa):
    data = {}
    response = jwt_authenticated_client_sme.post("/api/objetivos-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['nome'] == ["Nome do objetivo é obrigatório."]
    assert result.keys() == {'nome'}


@pytest.mark.django_db
def test_cria_objetivo_paa_com_nome_vazio(jwt_authenticated_client_sme, flag_paa):
    data = {'nome': ''}
    response = jwt_authenticated_client_sme.post("/api/objetivos-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['nome'] == ["Nome do objetivo não foi informado."]
    assert result.keys() == {'nome'}


@pytest.mark.django_db
def test_cria_objetivo_paa_com_sucesso(jwt_authenticated_client_sme, flag_paa, paa):
    data = {
        "paa": str(paa.uuid),
        "status": 1,
        "nome": "Teste"
    }
    response = jwt_authenticated_client_sme.post("/api/objetivos-paa/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert ObjetivoPaa.objects.count() == 1
    assert ObjetivoPaa.objects.filter(status=True, nome="Teste").count() == 1

    data = {
        "paa": str(paa.uuid),
        "status": 0,
        "nome": "Teste 2"
    }
    response = jwt_authenticated_client_sme.post("/api/objetivos-paa/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert ObjetivoPaa.objects.count() == 2
    assert ObjetivoPaa.objects.filter(status=False, nome="Teste 2").count() == 1


@pytest.mark.django_db
def test_patch_objetivo(jwt_authenticated_client_sme, objetivo_paa_factory):
    obj = objetivo_paa_factory.create(nome="Antigo Nome", paa=None)
    url = reverse("api:objetivos-paa-detail", args=[obj.uuid])
    response = jwt_authenticated_client_sme.patch(url, {"nome": "Nome Atualizado"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    obj.refresh_from_db()
    assert obj.nome == "Nome Atualizado"


@pytest.mark.django_db
def test_delete_objetivo(jwt_authenticated_client_sme, objetivo_paa_factory):
    obj = objetivo_paa_factory.create(nome="A Deletar", paa=None)
    url = reverse("api:objetivos-paa-detail", args=[obj.uuid])
    response = jwt_authenticated_client_sme.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ObjetivoPaa.objects.filter(uuid=obj.uuid).exists()


@pytest.mark.django_db
def test_filtrar_por_status(jwt_authenticated_client_sme, objetivo_paa_factory):
    objetivo_paa_factory.create(nome="Ativo", status=StatusChoices.ATIVO, paa=None)
    objetivo_paa_factory.create(nome="Inativo", status=StatusChoices.INATIVO, paa=None)

    url = reverse("api:objetivos-paa-list")
    response = jwt_authenticated_client_sme.get(url, {"status": StatusChoices.ATIVO})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["nome"] == "Ativo"


@pytest.mark.django_db
def test_endpoint_tabelas(jwt_authenticated_client_sme):
    url = reverse("api:objetivos-paa-tabelas")
    response = jwt_authenticated_client_sme.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.data
    assert any(item["value"] == "Ativo" for item in response.data["status"])
    assert any(item["value"] == "Inativo" for item in response.data["status"])
