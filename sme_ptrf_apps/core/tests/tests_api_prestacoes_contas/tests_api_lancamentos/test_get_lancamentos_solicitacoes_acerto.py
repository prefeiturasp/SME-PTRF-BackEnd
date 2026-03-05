import json

import pytest

from rest_framework import status


pytestmark = pytest.mark.django_db


def test_api_get_solicitacoes_acerto_de_um_lancamento(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    periodo_2020_1,
    conta_associacao_cartao,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    tipo_acerto_lancamento_basico,
    tipo_acerto_lancamento_devolucao,
    tipo_devolucao_ao_tesouro_teste,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    solicitacao_acerto_lancamento_devolucao,
    solicitacao_devolucao_ao_tesouro
):
    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/analises-de-lancamento/?analise_lancamento={analise_lancamento_despesa_prestacao_conta_2020_1_em_analise.uuid}'  # noqa
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result["analise_prestacao_conta"] == f'{analise_prestacao_conta_2020_1_em_analise.uuid}'
