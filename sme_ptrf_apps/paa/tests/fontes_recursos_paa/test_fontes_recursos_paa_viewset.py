import pytest
from rest_framework import status
from sme_ptrf_apps.paa.models import FonteRecursoPaa


@pytest.mark.django_db
def test_lista_fontes_recursos_paa(jwt_authenticated_client_sme, flag_paa, fonte_recurso_paa):

    response = jwt_authenticated_client_sme.get("/api/fontes-recursos-paa/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 10


@pytest.mark.django_db
def test_obtem_fonte_recurso_paa(jwt_authenticated_client_sme, flag_paa, fonte_recurso_paa):
    response = jwt_authenticated_client_sme.get(f"/api/fontes-recursos-paa/{fonte_recurso_paa.uuid}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Fonte recurso"


@pytest.mark.django_db
def test_cria_fonte_recurso_paa(jwt_authenticated_client_sme, flag_paa):
    data = {"nome": "Nova fonte recurso paa"}
    response = jwt_authenticated_client_sme.post("/api/fontes-recursos-paa/", data)

    assert response.status_code == status.HTTP_201_CREATED
    assert FonteRecursoPaa.objects.filter(nome="Nova fonte recurso paa").exists()


@pytest.mark.django_db
def test_cria_fonte_recurso_sem_nome(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.post("/api/fontes-recursos-paa/", {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data["nome"][0]) == "Nome da fonte de recurso paa é obrigatório."


@pytest.mark.django_db
def test_altera_fonte_recurso(jwt_authenticated_client_sme, fonte_recurso_paa, flag_paa):
    data = {"nome": "Novo Nome da fonte recurso"}
    response = jwt_authenticated_client_sme.patch(f"/api/fontes-recursos-paa/{fonte_recurso_paa.uuid}/", data)

    assert response.status_code == status.HTTP_200_OK, response.content
    fonte_recurso_paa.refresh_from_db()
    assert fonte_recurso_paa.nome == "Novo Nome da fonte recurso"
