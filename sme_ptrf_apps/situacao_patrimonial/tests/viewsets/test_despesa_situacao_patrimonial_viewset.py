import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def response_situacao_patrimonial(jwt_authenticated_client_sme, bem_produzido_despesa_1, flag_situacao_patrimonial, bem_produzido_rateio_1):
    url = f"/api/despesa-situacao-patrimonial/?associacao__uuid={bem_produzido_despesa_1.bem_produzido.associacao.uuid}"
    return jwt_authenticated_client_sme.get(url)


def test_get_sucesso(response_situacao_patrimonial):
    """Testa se a resposta retorna com sucesso e contém apenas um resultado."""
    content = response_situacao_patrimonial.data

    assert response_situacao_patrimonial.status_code == status.HTTP_200_OK, \
        f"Status esperado 200, obtido {response_situacao_patrimonial.status_code}"

    assert content["count"] == 1, f"Esperado count == 1, obtido {content['count']}"
    assert len(content["results"]) == 1, f"Esperado 1 resultado, obtido {len(content['results'])}"


def test_assert_valor_utilizado(response_situacao_patrimonial):
    """Verifica se o valor utilizado no rateio está correto."""
    valor_utilizado = response_situacao_patrimonial.data["results"][0]["rateios"][0]["valor_utilizado"]
    assert valor_utilizado == 120.0, f"Esperado valor_utilizado == 120.0, obtido {valor_utilizado}"


def test_assert_valor_disponivel(response_situacao_patrimonial):
    """Verifica se o valor disponível no rateio está correto."""
    valor_disponivel = response_situacao_patrimonial.data["results"][0]["rateios"][0]["valor_disponivel"]
    assert valor_disponivel == 80.0, f"Esperado valor_disponivel == 80.0, obtido {valor_disponivel}"
