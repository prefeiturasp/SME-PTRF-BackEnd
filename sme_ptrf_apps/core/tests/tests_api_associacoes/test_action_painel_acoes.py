import json
import datetime
import pytest

from freezegun import freeze_time

from rest_framework import status

pytestmark = pytest.mark.django_db

@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes(
    client,
    associacao,
    periodo_anterior,
    periodo, acao_associacao,
    receita_100_no_periodo,
    receita_50_fora_do_periodo,
    despesa_no_periodo,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_100_custeio,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio
):
    response = client.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas}',
        'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas}',
        'data_prevista_repasse': f'{periodo.data_prevista_repasse}',
        'ultima_atualizacao': f'{datetime.datetime(2020, 4, 18, 10, 11, 12)}',
        'info_acoes': [
            {
                'acao_associacao_uuid': f'{acao_associacao.uuid}',
                'acao_associacao_nome': acao_associacao.acao.nome,
                'saldo_reprogramado': 0,
                'receitas_no_periodo': 100.0,
                'repasses_no_periodo': 0,
                'despesas_no_periodo': 300.0,
                'saldo_atual_custeio': 0.0,
                'saldo_atual_capital': -200.0,
                'saldo_atual_total': -200.0,
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
