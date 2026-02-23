from datetime import date
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def cria_despesa(associacao, despesa_factory, rateio_despesa_factory, conta_associacao, acao_associacao, tipo_documento, tipo_transacao):
    def _cria(**kwargs):
        despesa = despesa_factory(
            associacao=associacao,
            **kwargs
        )

        rateio_despesa_factory(despesa=despesa, conta_associacao=conta_associacao, acao_associacao=acao_associacao)
        return despesa

    return _cria


def get_despesas(client, associacao, **params):
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"/api/despesas/?associacao__uuid={associacao.uuid}&{query}"
    response = client.get(url, content_type="application/json")
    assert response.status_code == status.HTTP_200_OK
    return response.json()["results"]


@pytest.mark.parametrize(
    "ordenacao, campo, esperado",
    [
        ("ordenar_por_numero_do_documento=crescente", "numero_documento", ["123456", "654321"]),
        ("ordenar_por_numero_do_documento=decrescente", "numero_documento", ["654321", "123456"]),
        ("ordenar_por_valor=crescente", "valor_total", ["100.00", "200.00"]),
        ("ordenar_por_valor=decrescente", "valor_total", ["200.00", "100.00"]),
        ("ordenar_por_data_especificacao=crescente", "data_documento", ["2020-03-10", "2020-03-11"]),
        ("ordenar_por_data_especificacao=decrescente", "data_documento", ["2020-03-11", "2020-03-10"]),
    ]
)
def test_api_ordenacao_simples(
    jwt_authenticated_client_d,
    associacao,
    cria_despesa,
    ordenacao,
    campo,
    esperado,
):
    cria_despesa(numero_documento="123456", data_documento=date(2020, 3, 10), valor_total=100)
    cria_despesa(numero_documento="654321", data_documento=date(2020, 3, 11), valor_total=200)

    result = get_despesas(jwt_authenticated_client_d, associacao, **dict(p.split("=") for p in [ordenacao]))

    assert [r[campo] for r in result] == esperado
