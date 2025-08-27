import datetime
import json

import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_de_uma_conta(
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
    conta_associacao
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/?conta={conta_associacao.uuid}',
                          content_type='application/json')
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
        'info_conta': {
            'conta_associacao_uuid': f'{conta_associacao.uuid}',
            'conta_associacao_nome': conta_associacao.tipo_conta.nome,

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
            'saldo_atual_total': 100.0

        },
        'prestacao_contas_status': {
            'documentos_gerados': False,
            'pc_requer_conclusao': True,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.',
            'prestacao_de_contas_uuid': None,
            'requer_retificacao': False,
            'tem_acertos_pendentes': False,
            'requer_acertos_em_extrato': False
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_de_uma_conta_tendo_outras_contas(
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
    conta_associacao,
    conta_associacao_cartao,
    rateio_no_periodo_1500_capital_outra_conta
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/?conta={conta_associacao.uuid}',
                          content_type='application/json')
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
        'info_conta': {
            'conta_associacao_uuid': f'{conta_associacao.uuid}',
            'conta_associacao_nome': conta_associacao.tipo_conta.nome,

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
            'saldo_atual_total': 100.0

        },
        'prestacao_contas_status': {
            'documentos_gerados': False,
            'pc_requer_conclusao': True,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.',
            'prestacao_de_contas_uuid': None,
            'requer_retificacao': False,
            'tem_acertos_pendentes': False,
            'requer_acertos_em_extrato': False
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_de_uma_conta_invalida(
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
    conta_associacao
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/painel-acoes/?conta=NAOEXISTE',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {'erro': 'UUID da conta inválido.'}

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result == esperado


@freeze_time('2020-04-18 10:11:12')
def test_action_painel_acoes_de_uma_periodo_invalida(
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
    conta_associacao
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/painel-acoes/?conta={conta_associacao.uuid}&periodo_uuid=INVALIDO',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {'erro': 'UUID do período inválido.'}

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result == esperado
