import datetime
import json

import pytest
from freezegun import freeze_time
from rest_framework import status

from ...status_periodo_associacao import STATUS_PERIODO_ASSOCIACAO_PENDENTE

pytestmark = pytest.mark.django_db


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes(
    client,
    associacao,
    periodo_anterior,
    periodo, acao_associacao,
    receita_100_no_periodo,
    receita_300_repasse_no_periodo,
    receita_50_fora_do_periodo,
    despesa_no_periodo,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_100_custeio,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio,
):
    response = client.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo.referencia,
        'periodo_status': STATUS_PERIODO_ASSOCIACAO_PENDENTE,
        'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas}',
        'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas}',
        'data_prevista_repasse': f'{periodo.data_prevista_repasse}',
        'ultima_atualizacao': f'{datetime.datetime(2020, 4, 18, 10, 11, 12)}',
        'info_acoes': [
            {
                'acao_associacao_uuid': f'{acao_associacao.uuid}',
                'acao_associacao_nome': acao_associacao.acao.nome,

                'saldo_reprogramado': 0,
                'saldo_reprogramado_capital': 0,
                'saldo_reprogramado_custeio': 0,
                'saldo_reprogramado_livre': 0,

                'receitas_no_periodo': 400.0,

                'repasses_no_periodo': 300.0,
                'repasses_no_periodo_capital': 0,
                'repasses_no_periodo_custeio': 300.0,
                'repasses_no_periodo_livre': 0,

                'outras_receitas_no_periodo': 100.0,
                'outras_receitas_no_periodo_capital': 0,
                'outras_receitas_no_periodo_custeio': 100.0,
                'outras_receitas_no_periodo_livre': 0,

                'despesas_no_periodo': 300.0,
                'despesas_no_periodo_capital': 200.0,
                'despesas_no_periodo_custeio': 100.0,

                'saldo_atual_custeio': 300.0,
                'saldo_atual_capital': -200.0,
                'saldo_atual_livre': 0,
                'saldo_atual_total': 100.0,

                'despesas_nao_conciliadas': 300.0,
                'despesas_nao_conciliadas_capital': 200.0,
                'despesas_nao_conciliadas_custeio': 100.0,

                'receitas_nao_conciliadas': 400.0,
                'receitas_nao_conciliadas_capital': 0,
                'receitas_nao_conciliadas_custeio': 400.0,
                'receitas_nao_conciliadas_livre': 0,

                'especificacoes_despesas_capital': ['Ar condicionado', ],
                'especificacoes_despesas_custeio': ['Material elétrico'],

                'repasses_nao_realizados_capital': 0.0,
                'repasses_nao_realizados_custeio': 0.0,
                'repasses_nao_realizados_livre': 0.0
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_por_periodo(
    client,
    associacao,
    periodo_anterior,
    fechamento_periodo_anterior,
    periodo, acao_associacao,
    receita_100_no_periodo,
    receita_300_repasse_no_periodo,
    receita_50_fora_do_periodo,
    despesa_no_periodo,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_100_custeio,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio,
):
    response = client.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/?periodo_uuid={periodo_anterior.uuid}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo_anterior.referencia,
        'periodo_status': STATUS_PERIODO_ASSOCIACAO_PENDENTE,
        'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
        'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
        'data_prevista_repasse': f'{periodo_anterior.data_prevista_repasse}',
        'ultima_atualizacao': f'{datetime.datetime(2020, 4, 18, 10, 11, 12)}',
        'info_acoes': [
            {
                'acao_associacao_uuid': f'{acao_associacao.uuid}',
                'acao_associacao_nome': acao_associacao.acao.nome,

                'saldo_reprogramado': 0.0,
                'saldo_reprogramado_capital': 0,
                'saldo_reprogramado_custeio': 0,
                'saldo_reprogramado_livre': 0,

                'receitas_no_periodo': 3500.0,

                'repasses_no_periodo': 3350.0,
                'repasses_no_periodo_capital': 450.0,
                'repasses_no_periodo_custeio': 900.0,
                'repasses_no_periodo_livre': 2000,

                'outras_receitas_no_periodo': 150.0,
                'outras_receitas_no_periodo_capital': 50.0,
                'outras_receitas_no_periodo_custeio': 100.0,
                'outras_receitas_no_periodo_livre': 0,

                'despesas_no_periodo': 1200.0,
                'despesas_no_periodo_capital': 400.0,
                'despesas_no_periodo_custeio': 800.0,

                'saldo_atual_custeio': 200.0,
                'saldo_atual_capital': 100.0,
                'saldo_atual_livre': 2000,
                'saldo_atual_total': 2300.0,

                'despesas_nao_conciliadas': 0.0,
                'despesas_nao_conciliadas_capital': 0.0,
                'despesas_nao_conciliadas_custeio': 0.0,

                'receitas_nao_conciliadas': 0.0,
                'receitas_nao_conciliadas_capital': 0.0,
                'receitas_nao_conciliadas_custeio': 0.0,
                'receitas_nao_conciliadas_livre': 0.0,

                'especificacoes_despesas_capital': [],
                'especificacoes_despesas_custeio': [],

                'repasses_nao_realizados_capital': 0.0,
                'repasses_nao_realizados_custeio': 0.0,
                'repasses_nao_realizados_livre': 0.0
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_deve_atender_a_ordem_das_acoes(
    client,
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    acao_associacao_de_destaque,
    receita_100_no_periodo,
    receita_100_no_periodo_acao_de_destaque,
):
    response = client.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo.referencia,
        'periodo_status': STATUS_PERIODO_ASSOCIACAO_PENDENTE,
        'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas}',
        'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas}',
        'data_prevista_repasse': f'{periodo.data_prevista_repasse}',
        'ultima_atualizacao': f'{datetime.datetime(2020, 4, 18, 10, 11, 12)}',
        'info_acoes': [
            {
                'acao_associacao_uuid': f'{acao_associacao_de_destaque.uuid}',
                'acao_associacao_nome': acao_associacao_de_destaque.acao.nome,

                'saldo_reprogramado': 0,
                'saldo_reprogramado_capital': 0,
                'saldo_reprogramado_custeio': 0,
                'saldo_reprogramado_livre': 0,

                'receitas_no_periodo': 100.0,

                'repasses_no_periodo': 0,
                'repasses_no_periodo_capital': 0,
                'repasses_no_periodo_custeio': 0,
                'repasses_no_periodo_livre': 0,

                'outras_receitas_no_periodo': 100.0,
                'outras_receitas_no_periodo_capital': 0,
                'outras_receitas_no_periodo_custeio': 100.0,
                'outras_receitas_no_periodo_livre': 0,

                'despesas_no_periodo': 0,
                'despesas_no_periodo_capital': 0,
                'despesas_no_periodo_custeio': 0,

                'saldo_atual_custeio': 100.0,
                'saldo_atual_capital': 0,
                'saldo_atual_livre': 0,
                'saldo_atual_total': 100.0,

                'despesas_nao_conciliadas': 0,
                'despesas_nao_conciliadas_capital': 0,
                'despesas_nao_conciliadas_custeio': 0,

                'receitas_nao_conciliadas': 100.0,
                'receitas_nao_conciliadas_capital': 0,
                'receitas_nao_conciliadas_custeio': 100.0,
                'receitas_nao_conciliadas_livre': 0,

                'especificacoes_despesas_capital': [],
                'especificacoes_despesas_custeio': [],

                'repasses_nao_realizados_capital': 0.0,
                'repasses_nao_realizados_custeio': 0.0,
                'repasses_nao_realizados_livre': 0.0
            },
            {
                'acao_associacao_uuid': f'{acao_associacao.uuid}',
                'acao_associacao_nome': acao_associacao.acao.nome,

                'saldo_reprogramado': 0,

                'saldo_reprogramado_capital': 0,
                'saldo_reprogramado_custeio': 0,
                'saldo_reprogramado_livre': 0,

                'receitas_no_periodo': 100.0,

                'repasses_no_periodo': 0,
                'repasses_no_periodo_capital': 0,
                'repasses_no_periodo_custeio': 0,
                'repasses_no_periodo_livre': 0,

                'outras_receitas_no_periodo': 100.0,
                'outras_receitas_no_periodo_capital': 0,
                'outras_receitas_no_periodo_custeio': 100.0,
                'outras_receitas_no_periodo_livre': 0,

                'despesas_no_periodo': 0,
                'despesas_no_periodo_capital': 0,
                'despesas_no_periodo_custeio': 0,

                'saldo_atual_custeio': 100.0,
                'saldo_atual_capital': 0,
                'saldo_atual_livre': 0,
                'saldo_atual_total': 100.0,

                'despesas_nao_conciliadas': 0,
                'despesas_nao_conciliadas_capital': 0,
                'despesas_nao_conciliadas_custeio': 0,

                'receitas_nao_conciliadas': 100.0,
                'receitas_nao_conciliadas_capital': 0,
                'receitas_nao_conciliadas_custeio': 100.0,
                'receitas_nao_conciliadas_livre': 0,

                'especificacoes_despesas_capital': [],
                'especificacoes_despesas_custeio': [],

                'repasses_nao_realizados_capital': 0.0,
                'repasses_nao_realizados_custeio': 0.0,
                'repasses_nao_realizados_livre': 0.0
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
