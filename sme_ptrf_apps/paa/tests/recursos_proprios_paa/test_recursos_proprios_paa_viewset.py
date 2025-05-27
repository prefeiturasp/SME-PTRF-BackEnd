import pytest
from rest_framework import status
from sme_ptrf_apps.paa.models import RecursoProprioPaa


@pytest.mark.django_db
def test_lista_recursos_proprios_paa(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa):

    response = jwt_authenticated_client_sme.get("/api/recursos-proprios-paa/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_obter_recurso_proprio_paa(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa_factory):
    recurso = recurso_proprio_paa_factory.create(descricao="ABC 007", valor=100.00)

    response = jwt_authenticated_client_sme.get(f"/api/recursos-proprios-paa/{recurso.uuid}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["descricao"] == "ABC 007"
    assert response.data["valor"] == 100.00


@pytest.mark.django_db
def test_obter_recurso_proprio_paa_404(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa_factory):
    recurso_proprio_paa_factory.create(descricao="ABC 007", valor=100.00)

    response = jwt_authenticated_client_sme.get("/api/recursos-proprios-paa/a41efdd4-068b-43a8-9211-9339bceda4d8/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_cria_recurso_proprio_paa(jwt_authenticated_client_sme, flag_paa, associacao, fonte_recurso_paa, paa):
    data = {
        "paa": str(paa.uuid),
        "fonte_recurso": str(fonte_recurso_paa.uuid),
        "associacao": str(associacao.uuid),
        "data_prevista": "2024-04-04",
        "descricao": "Descricao 007",
        "valor": 150.99
    }
    response = jwt_authenticated_client_sme.post("/api/recursos-proprios-paa/", data)

    assert response.status_code == status.HTTP_201_CREATED
    assert RecursoProprioPaa.objects.filter(
        associacao=associacao,
        fonte_recurso=fonte_recurso_paa,
        descricao="Descricao 007").exists()


@pytest.mark.django_db
def test_cria_recurso_proprio_paa_campos_faltando(jwt_authenticated_client_sme,
                                                  flag_paa, associacao, fonte_recurso_paa):
    data = {
        "fonte_recurso": str(fonte_recurso_paa.uuid),
        "associacao": str(associacao.uuid),
        "data_prevista": "2024-04-04",
        "valor": 150.99
    }
    response = jwt_authenticated_client_sme.post("/api/recursos-proprios-paa/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not RecursoProprioPaa.objects.filter(
        associacao=associacao,
        fonte_recurso=fonte_recurso_paa,
        descricao="Descricao 007").exists()


@pytest.mark.django_db
def test_atualiza_recurso_proprio_paa(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa):
    data = {
        "data_prevista": "2024-04-29",
        "descricao": "Descricao 007006"
    }
    response = jwt_authenticated_client_sme.patch(f"/api/recursos-proprios-paa/{recurso_proprio_paa.uuid}/", data)

    assert response.status_code == status.HTTP_200_OK
    assert RecursoProprioPaa.objects.filter(
        descricao="Descricao 007006").exists()


@pytest.mark.django_db
def test_atualiza_recurso_proprio_paa_404(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa):
    data = {
        "data_prevista": "2024-04-29",
        "descricao": "Descricao 007006"
    }
    response = jwt_authenticated_client_sme.patch(
        "/api/recursos-proprios-paa/a41efdd4-068b-43a8-9211-9339bceda4d8/", data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not RecursoProprioPaa.objects.filter(
        descricao="Descricao 007006").exists()


@pytest.mark.django_db
def test_exclui_recurso_proprio_paa(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa):
    response = jwt_authenticated_client_sme.delete(f"/api/recursos-proprios-paa/{recurso_proprio_paa.uuid}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not RecursoProprioPaa.objects.filter(
        descricao=recurso_proprio_paa.descricao).exists()


@pytest.mark.django_db
def test_obter_total_recurso_proprio_paa(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa_factory):
    recurso_proprio_paa_factory.create(descricao="ABC 004", valor=100.00)
    recurso_proprio_paa_factory.create(descricao="ABC 005", valor=200.00)
    recurso_proprio_paa_factory.create(descricao="ABC 006", valor=300.00)
    recurso_proprio_paa_factory.create(descricao="ABC 007", valor=150.00)

    response = jwt_authenticated_client_sme.get("/api/recursos-proprios-paa/total/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total"] == 750.00
