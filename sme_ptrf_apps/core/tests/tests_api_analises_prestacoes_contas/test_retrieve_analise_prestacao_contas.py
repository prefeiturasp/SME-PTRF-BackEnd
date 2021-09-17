import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_retrieve_analise_prestacao_contas_existente(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    solicitacao_acerto_documento_ata_teste_analises,
    solicitacao_acerto_documento_declaracao_cartao_teste_analises,
    solicitacao_acerto_lancamento_devolucao_teste_analises


):
    analise_prestacao = solicitacao_acerto_documento_ata_teste_analises.analise_documento.analise_prestacao_conta

    result_esperado = {}

    url = f'/api/analises-prestacoes-contas/{analise_prestacao.uuid}/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
