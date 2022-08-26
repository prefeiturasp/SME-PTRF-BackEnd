import datetime
import json

import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
    receita_300_repasse_no_periodo,
    receita_50_fora_do_periodo,
    despesa_no_periodo,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_100_custeio,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio,
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo.referencia,
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
                'saldo_atual_capital': 0.0,
                'saldo_atual_livre': -200,
                'saldo_atual_total': 100.0,

            }
        ],
        'info_conta': None,
        'prestacao_contas_status': {
            'documentos_gerados': None,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.',
            'prestacao_de_contas_uuid': None,
            'requer_retificacao': False,

        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_por_periodo(
    jwt_authenticated_client_a,
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
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/?periodo_uuid={periodo_anterior.uuid}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo_anterior.referencia,
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

            }
        ],
        'info_conta': None,
        'prestacao_contas_status': {
            'documentos_gerados': None,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.',
            'prestacao_de_contas_uuid': None,
            'requer_retificacao': False,
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_deve_atender_a_ordem_das_acoes(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    acao_associacao_de_destaque,
    receita_100_no_periodo,
    receita_100_no_periodo_acao_de_destaque,
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo.referencia,
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

            }
        ],
        'info_conta': None,
        'prestacao_contas_status': {
            'documentos_gerados': None,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.',
            'prestacao_de_contas_uuid': None,
            'requer_retificacao': False,
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
