import pytest
from rest_framework import status
from ...models import ReceitaPrevistaPdde


@pytest.mark.django_db
def test_cria_receita_prevista_pdde(jwt_authenticated_client_sme, acao_pdde, flag_paa, paa):
    data = {"paa": str(paa.uuid), "previsao_valor_custeio": 1234, "acao_pdde": acao_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/receitas-previstas-pdde/", data)

    assert response.status_code == status.HTTP_201_CREATED, response.content
    assert ReceitaPrevistaPdde.objects.filter(acao_pdde=acao_pdde, previsao_valor_custeio=1234).exists()


@pytest.mark.django_db
def test_cria_receita_prevista_pdde_sem_acao_pdde_e_sem_paa(jwt_authenticated_client_sme, flag_paa):
    data = {"previsao_valor_custeio": 2000}
    response = jwt_authenticated_client_sme.post("/api/receitas-previstas-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'acao_pdde' in response.data
    assert 'paa' in response.data
