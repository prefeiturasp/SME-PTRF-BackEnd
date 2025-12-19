import pytest
from django.urls import reverse
from rest_framework import status
from ...models import OutroRecursoPeriodoPaa
from sme_ptrf_apps.core.fixtures.factories import FlagFactory, UnidadeFactory
from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoPeriodoFactory

BASE_URL = reverse("api:outros-recursos-periodos-paa-list")


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_outros_recursos_periodo(jwt_authenticated_client_sme, flag_paa, periodo_paa, outro_recurso_factory):
    for index in range(20):
        recurso = outro_recurso_factory.create(nome=f"Outro-Recurso-{index + 1}")
        OutroRecursoPeriodoFactory.create(outro_recurso=recurso, periodo_paa=periodo_paa)

    response = jwt_authenticated_client_sme.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 20
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]
    assert response.data["links"]['next'] is not None


@pytest.mark.django_db
def test_obtem_outro_recurso_periodo_paa_por_uuid(jwt_authenticated_client_sme, outros_recursos_periodo, flag_paa):
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[outros_recursos_periodo.uuid])
    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["periodo_paa"] == outros_recursos_periodo.periodo_paa.uuid
    assert response.data["outro_recurso"] == outros_recursos_periodo.outro_recurso.uuid
    assert response.data["ativo"] is True


@pytest.mark.django_db
def test_obtem_outro_recurso_periodo_paa_por_periodo_e_recurso(jwt_authenticated_client_sme, outros_recursos_periodo,
                                                               flag_paa):
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[outros_recursos_periodo.uuid])
    params = {
        "periodo_paa": outros_recursos_periodo.periodo_paa.uuid,
        "outro_recurso": outros_recursos_periodo.outro_recurso.uuid
    }
    response = jwt_authenticated_client_sme.get(url, params)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["periodo_paa"] == outros_recursos_periodo.periodo_paa.uuid
    assert response.data["outro_recurso"] == outros_recursos_periodo.outro_recurso.uuid
    assert response.data["ativo"] is True


@pytest.mark.django_db
def test_cria_outros_recursos_periodo(jwt_authenticated_client_sme, flag_paa, periodo_paa, outro_recurso):
    data = {
        "periodo_paa": periodo_paa.uuid,
        "outro_recurso": outro_recurso.uuid,
    }
    response = jwt_authenticated_client_sme.post(BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert OutroRecursoPeriodoPaa.objects.filter(periodo_paa=periodo_paa, outro_recurso=outro_recurso).exists()


@pytest.mark.django_db
def test_cria_outros_recursos_periodo_duplicado(jwt_authenticated_client_sme, outros_recursos_periodo, flag_paa):
    data = {
        "periodo_paa": outros_recursos_periodo.periodo_paa.uuid,
        "outro_recurso": outros_recursos_periodo.outro_recurso.uuid,
    }
    response = jwt_authenticated_client_sme.post(BASE_URL, data)
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in result
    assert result["non_field_errors"] == ["Já existe um Recurso cadastrado para o período informado."]


@pytest.mark.django_db
def test_altera_outros_recursos_periodo(jwt_authenticated_client_sme, outros_recursos_periodo, flag_paa):
    assert outros_recursos_periodo.ativo is True
    data = {"ativo": False}
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[outros_recursos_periodo.uuid])
    response = jwt_authenticated_client_sme.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    outros_recursos_periodo.refresh_from_db()
    assert outros_recursos_periodo.ativo is False


@pytest.mark.django_db
def test_exclui_outros_recursos_periodo(jwt_authenticated_client_sme, flag_paa):
    remover = OutroRecursoPeriodoFactory()
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[remover.uuid])
    response = jwt_authenticated_client_sme.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not OutroRecursoPeriodoPaa.objects.filter(uuid=remover.uuid).exists()


@pytest.mark.django_db
def test_exclui_outros_recursos_periodos_inexistente(jwt_authenticated_client_sme, flag_paa):
    """Testa a exclusão de um recurso periodo que não existe"""
    from uuid import uuid4
    uuid_inexistente = uuid4()
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[uuid_inexistente])
    response = jwt_authenticated_client_sme.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_importar_unidades_com_sucesso(
    jwt_authenticated_client_sme,
    periodo_paa,
):
    # Origem com unidades
    unidades = UnidadeFactory.create_batch(3)

    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )
    origem.unidades.add(*unidades)

    destino = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )

    url = reverse("api:outros-recursos-periodos-paa-importar-unidades", args=[destino.uuid])
    response = jwt_authenticated_client_sme.post(
        url,
        data={"origem_uuid": origem.uuid},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    destino.refresh_from_db()
    assert destino.unidades.count() == 3

    for unidade in unidades:
        assert unidade in destino.unidades.all()


@pytest.mark.django_db
def test_importar_unidades_sem_origem_uuid(
    jwt_authenticated_client_sme,
    periodo_paa,
):
    destino = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )

    url = reverse("api:outros-recursos-periodos-paa-importar-unidades", args=[destino.uuid])

    response = jwt_authenticated_client_sme.post(
        url,
        data={},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "origem_uuid é obrigatório."


@pytest.mark.django_db
def test_importar_unidades_origem_inexistente(
    jwt_authenticated_client_sme,
    periodo_paa,
):
    destino = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )

    url = reverse("api:outros-recursos-periodos-paa-importar-unidades", args=[destino.uuid])

    response = jwt_authenticated_client_sme.post(
        url,
        data={"origem_uuid": "00000000-0000-0000-0000-000000000000"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Recurso de origem não encontrado."
