import pytest
from rest_framework import status
from ...models import ReceitaPrevistaPaa
from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from sme_ptrf_apps.paa.fixtures.factories import ReceitaPrevistaPaaFactory


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_receita_prevista_paa(jwt_authenticated_client_sme, acao_associacao, flag_paa):

    for index in range(50):
        ReceitaPrevistaPaaFactory.create(
            acao_associacao=acao_associacao,
            previsao_valor_custeio=100 + index,
            previsao_valor_capital=101 + index,
            previsao_valor_livre=102 + index
        )

    response = jwt_authenticated_client_sme.get("/api/receitas-previstas-paa/?acao_nome=PTRF")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 50
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]
    assert response.data["links"]['next'] is not None


@pytest.mark.django_db
def test_obtem_receita_prevista_paa(jwt_authenticated_client_sme, receita_prevista_paa, flag_paa):
    response = jwt_authenticated_client_sme.get(f"/api/receitas-previstas-paa/{receita_prevista_paa.uuid}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["previsao_valor_custeio"] == "1000.00", response.data["previsao_valor_custeio"]
    assert response.data["previsao_valor_capital"] == "2000.00", response.data["previsao_valor_capital"]
    assert response.data["previsao_valor_livre"] == "3000.00", response.data["previsao_valor_livre"]


@pytest.mark.django_db
def test_cria_receita_prevista_paa(jwt_authenticated_client_sme, acao_associacao, flag_paa, paa):
    data = {"paa": str(paa.uuid), "previsao_valor_custeio": 1234, "acao_associacao": acao_associacao.uuid}
    response = jwt_authenticated_client_sme.post("/api/receitas-previstas-paa/", data)

    assert response.status_code == status.HTTP_201_CREATED, response.content
    assert ReceitaPrevistaPaa.objects.filter(acao_associacao=acao_associacao, previsao_valor_custeio=1234).exists()


@pytest.mark.django_db
def test_cria_receita_prevista_paa_sem_acao_associacao_e_sem_paa(jwt_authenticated_client_sme, flag_paa):
    data = {"previsao_valor_custeio": 2000}
    response = jwt_authenticated_client_sme.post("/api/receitas-previstas-paa/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'acao_associacao' in response.data
    assert 'paa' in response.data


@pytest.mark.django_db
def test_altera_receita_prevista_paa(jwt_authenticated_client_sme, receita_prevista_paa, flag_paa):
    valor_original = receita_prevista_paa.previsao_valor_custeio
    valor_alterado = 5000
    data = {"previsao_valor_custeio": valor_alterado}
    response = jwt_authenticated_client_sme.patch(f"/api/receitas-previstas-paa/{receita_prevista_paa.uuid}/", data)

    assert response.status_code == status.HTTP_200_OK, response.data
    receita_prevista_paa.refresh_from_db()
    assert receita_prevista_paa.previsao_valor_custeio == 5000
    assert receita_prevista_paa.previsao_valor_custeio != valor_original


@pytest.mark.django_db
def test_exclui_receita_prevista_paa(jwt_authenticated_client_sme, flag_paa, receita_prevista_paa):
    response = jwt_authenticated_client_sme.delete(f"/api/receitas-previstas-paa/{receita_prevista_paa.uuid}/")
    # não permitir e exclusão de registros
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
