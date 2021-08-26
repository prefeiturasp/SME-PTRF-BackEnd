import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_post_lancamentos_marcar_como_corretos(
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
):
    conta_uuid = conta_associacao_cartao.uuid

    payload = {
        'analise_prestacao': f'{analise_prestacao_conta_2020_1_em_analise.uuid}',
        'lancamentos_corretos': [
            {
                'tipo_lancamento': 'CREDITO',
                'lancamento': f'{receita_2020_1_ptrf_repasse_conferida.uuid}',
            },
            {
                'tipo_lancamento': 'GASTO',
                'lancamento': f'{despesa_2020_1.uuid}',
            },
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/lancamentos-corretos/'

    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Lançamentos marcados como corretos.'}

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 2
