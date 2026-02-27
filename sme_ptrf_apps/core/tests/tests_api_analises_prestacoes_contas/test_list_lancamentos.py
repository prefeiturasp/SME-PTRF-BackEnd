import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def retorna_tags_de_informacao(lancamento):
    informacoes = []
    if lancamento and lancamento['mestre'] and lancamento['mestre'].tags_de_informacao:
        for tag in lancamento['mestre'].tags_de_informacao:
            informacoes.append(tag)

    return informacoes


def retorna_tags_de_informacao_concatenadas(lancamento):
    if lancamento and lancamento['mestre'] and lancamento['mestre'].tags_de_informacao_concatenadas:
        return lancamento['mestre'].tags_de_informacao_concatenadas


def get_lancamentos(client, analise_uuid, conta_uuid, extra=""):
    url = (
        f"/api/analises-prestacoes-contas/{analise_uuid}/"
        f"lancamentos-com-ajustes/?conta_associacao={conta_uuid}{extra}"
    )
    response = client.get(url, content_type="application/json")
    assert response.status_code == status.HTTP_200_OK
    return response.json()


def test_api_list_lancamentos_todos_da_conta(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_analises,
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises
):
    result = get_lancamentos(
        jwt_authenticated_client_a,
        analise_prestacao_conta_2020_1_teste_analises.uuid,
        conta_associacao_cartao.uuid,
    )

    assert len(result) == 1

    lancamento = result[0]
    assert lancamento["tipo_transacao"] == "Gasto"
    assert lancamento["conta"] == str(conta_associacao_cartao.uuid)
    assert lancamento["documento_mestre"]["uuid"] == str(despesa_2020_1.uuid)


def test_api_list_lancamentos_todos_da_conta_inativa(
    jwt_authenticated_client_a,
    despesa_2020_1_inativa,
    rateio_despesa_2020_role_conferido_inativa,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_inativa_analises,
    analise_lancamento_despesa_inativa_prestacao_conta_2020_1_teste_analises
):
    result = get_lancamentos(
        jwt_authenticated_client_a,
        analise_prestacao_conta_2020_1_teste_inativa_analises.uuid,
        conta_associacao_cartao.uuid,
    )

    assert len(result) == 1

    documento = result[0]["documento_mestre"]
    assert documento["mensagem_inativa"] is not None
    assert "Este gasto foi excluído em" in documento["mensagem_inativa"]


def test_api_list_lancamentos_por_tipo_ajuste(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_analises,
    tipo_acerto_lancamento_devolucao,
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
    solicitacao_acerto_lancamento_devolucao_teste_analises,
    solicitacao_devolucao_ao_tesouro_teste_analises
):
    result = get_lancamentos(
        jwt_authenticated_client_a,
        analise_prestacao_conta_2020_1_teste_analises.uuid,
        conta_associacao_cartao.uuid,
        extra=f"&tipo_acerto={tipo_acerto_lancamento_devolucao.uuid}",
    )

    assert len(result) == 1
    assert result[0]["documento_mestre"]["uuid"] == str(despesa_2020_1.uuid)
