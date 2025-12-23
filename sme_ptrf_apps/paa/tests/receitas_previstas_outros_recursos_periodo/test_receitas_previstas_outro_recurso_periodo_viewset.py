import pytest
from rest_framework import status
from django.urls import reverse
from ...models import ReceitaPrevistaOutroRecursoPeriodo
from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from sme_ptrf_apps.paa.fixtures.factories import ReceitaPrevistaOutroRecursoPeriodoFactory

BASE_URL = reverse("api:receitas-previstas-outros-recursos-periodo-list")


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_receita_prevista_outro_recurso_periodo(
        jwt_authenticated_client_sme, outro_recurso_periodo_factory, paa_factory, periodo_paa_1, flag_paa):
    paa = paa_factory(periodo_paa=periodo_paa_1)
    for index in range(50):
        ReceitaPrevistaOutroRecursoPeriodoFactory.create(
            paa=paa,
            outro_recurso_periodo=outro_recurso_periodo_factory(periodo_paa=periodo_paa_1),
            previsao_valor_custeio=100 + index,
            previsao_valor_capital=100 + index,
            previsao_valor_livre=100 + index
        )

    response = jwt_authenticated_client_sme.get(BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 50
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]
    assert response.data["links"]['next'] is not None


@pytest.mark.django_db
def test_obtem_receita_prevista_outro_recurso_periodo(
        jwt_authenticated_client_sme, receita_prevista_outro_recurso_periodo, flag_paa):
    url = reverse(
        "api:receitas-previstas-outros-recursos-periodo-detail",
        args=[receita_prevista_outro_recurso_periodo.uuid])
    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["previsao_valor_custeio"] == "101.00", response.data["previsao_valor_custeio"]
    assert response.data["previsao_valor_capital"] == "102.00", response.data["previsao_valor_capital"]
    assert response.data["previsao_valor_livre"] == "103.00", response.data["previsao_valor_livre"]


@pytest.mark.django_db
def test_cria_receita_prevista_outro_recurso_periodo(
        jwt_authenticated_client_sme, outro_recurso_periodo, flag_paa, paa):
    data = {
        "paa": str(paa.uuid),
        "outro_recurso_periodo": outro_recurso_periodo.uuid,
        "previsao_valor_custeio": 1234,
    }
    response = jwt_authenticated_client_sme.post(BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED, response.content
    assert ReceitaPrevistaOutroRecursoPeriodo.objects.filter(
        outro_recurso_periodo=outro_recurso_periodo,
        previsao_valor_custeio=1234).exists()


@pytest.mark.django_db
def test_cria_receita_prevista_outro_recurso_periodo_sem_outro_recurso_periodo_e_sem_paa(
        jwt_authenticated_client_sme, flag_paa):
    data = {"previsao_valor_custeio": 2000}
    response = jwt_authenticated_client_sme.post(BASE_URL, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'outro_recurso_periodo' in response.data
    assert response.data['outro_recurso_periodo'] == ['Outro Recurso do Período não foi informado.']
    assert 'paa' in response.data
    assert response.data['paa'] == ['PAA não foi informado.'], response.data['paa']


@pytest.mark.django_db
def test_altera_receita_prevista_outro_recurso_periodo(
        jwt_authenticated_client_sme, receita_prevista_outro_recurso_periodo, flag_paa):
    url = reverse(
        "api:receitas-previstas-outros-recursos-periodo-detail",
        args=[receita_prevista_outro_recurso_periodo.uuid])
    valor_original = receita_prevista_outro_recurso_periodo.previsao_valor_custeio
    valor_alterado = 5000
    data = {"previsao_valor_custeio": valor_alterado}
    response = jwt_authenticated_client_sme.patch(url, data)

    assert response.status_code == status.HTTP_200_OK, response.data

    assert receita_prevista_outro_recurso_periodo.previsao_valor_custeio == valor_original

    receita_prevista_outro_recurso_periodo.refresh_from_db()
    assert receita_prevista_outro_recurso_periodo.previsao_valor_custeio == valor_alterado


@pytest.mark.django_db
def test_exclui_receita_prevista_outro_recurso_periodo(
        jwt_authenticated_client_sme, flag_paa, receita_prevista_outro_recurso_periodo):
    url = reverse(
        "api:receitas-previstas-outros-recursos-periodo-detail",
        args=[receita_prevista_outro_recurso_periodo.uuid])
    response = jwt_authenticated_client_sme.delete(url)
    # não permitir e exclusão de registros via API
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
