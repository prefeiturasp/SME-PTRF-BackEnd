import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_previa_info_para_ata(
    jwt_authenticated_client_a,
    associacao,
    acao_associacao_ptrf,
    periodo_2020_1,
    conta_associacao_cartao,
    fechamento_periodo_2019_2_1000,
    receita_2020_1_ptrf_repasse_conferida,
    despesa_2020_1,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_ptrf_nao_conferido,
    rateio_despesa_2019_ptrf_nao_conferido
):
    associacao_uuid = associacao.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/previa-info-para-ata/?associacao={associacao_uuid}&periodo={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    totais_esperados = {
        'saldo_reprogramado': 1000.0,
        'saldo_reprogramado_capital': 1000.0,
        'saldo_reprogramado_custeio': 0.0,
        'saldo_reprogramado_livre': 0.0,

        'receitas_no_periodo': 100.0,

        'receitas_devolucao_no_periodo': 0,
        'receitas_devolucao_no_periodo_capital': 0,
        'receitas_devolucao_no_periodo_custeio': 0,
        'receitas_devolucao_no_periodo_livre': 0,

        'repasses_no_periodo': 100.0,
        'repasses_no_periodo_capital': 0,
        'repasses_no_periodo_custeio': 100.0,
        'repasses_no_periodo_livre': 0,

        'outras_receitas_no_periodo': 0.0,
        'outras_receitas_no_periodo_capital': 0,
        'outras_receitas_no_periodo_custeio': 0.0,
        'outras_receitas_no_periodo_livre': 0,

        'despesas_no_periodo': 80.0,
        'despesas_no_periodo_capital': 0,
        'despesas_no_periodo_custeio': 80.0,
        'despesas_nao_conciliadas': 40.0,
        'despesas_nao_conciliadas_capital': 0,
        'despesas_nao_conciliadas_custeio': 40.0,

        'despesas_conciliadas': 40.0,
        'despesas_conciliadas_capital': 0,
        'despesas_conciliadas_custeio': 40.0,

        'despesas_nao_conciliadas_anteriores': 10.0,
        'despesas_nao_conciliadas_anteriores_capital': 0,
        'despesas_nao_conciliadas_anteriores_custeio': 10.0,

        'receitas_nao_conciliadas': 0,
        'receitas_nao_conciliadas_capital': 0,
        'receitas_nao_conciliadas_custeio': 0,
        'receitas_nao_conciliadas_livre': 0,

        'saldo_atual_capital': 1000.0,
        'saldo_atual_custeio': 20.0,
        'saldo_atual_livre': 0.0,
        'saldo_atual_total': 1020.0,

        'repasses_nao_realizados_capital': 0,
        'repasses_nao_realizados_custeio': 0,
        'repasses_nao_realizados_livre': 0,

        # Saldo Atual + Despesas Não demonstradas no período + Despesas não demonstradas períodos anteriores
        'saldo_bancario_capital': 1000.0,
        'saldo_bancario_custeio': 70,
        'saldo_bancario_livre': 0.0,
        'saldo_bancario_total': 1070.0,
    }

    info_contas_esperadas = [
        {

            'conta_associacao': {'agencia': '',
                                 'banco_nome': '',
                                 'nome': 'Cartão',
                                 'numero_conta': '',
                                 'uuid': f'{conta_associacao_cartao.uuid}'},
            'acoes': [
                {
                    'acao_associacao_nome': 'PTRF',
                    'acao_associacao_uuid': f'{acao_associacao_ptrf.uuid}',
                    'saldo_reprogramado': 1000.0,
                    'saldo_reprogramado_capital': 1000.0,
                    'saldo_reprogramado_custeio': 0.0,
                    'saldo_reprogramado_livre': 0.0,
                    'despesas_nao_conciliadas': 40.0,
                    'despesas_nao_conciliadas_capital': 0,
                    'despesas_nao_conciliadas_custeio': 40.,
                    'despesas_conciliadas': 40.0,
                    'despesas_conciliadas_capital': 0,
                    'despesas_conciliadas_custeio': 40.0,
                    'despesas_nao_conciliadas_anteriores': 10,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 10,
                    'despesas_no_periodo': 80.0,
                    'despesas_no_periodo_capital': 0,
                    'despesas_no_periodo_custeio': 80.0,
                    'especificacoes_despesas_capital': [],
                    'especificacoes_despesas_custeio': ['Instalação elétrica'],
                    'outras_receitas_no_periodo': 0.0,
                    'outras_receitas_no_periodo_capital': 0,
                    'outras_receitas_no_periodo_custeio': 0.0,
                    'outras_receitas_no_periodo_livre': 0,
                    'receitas_devolucao_no_periodo': 0,
                    'receitas_devolucao_no_periodo_capital': 0,
                    'receitas_devolucao_no_periodo_custeio': 0,
                    'receitas_devolucao_no_periodo_livre': 0,
                    'receitas_nao_conciliadas': 0,
                    'receitas_nao_conciliadas_capital': 0,
                    'receitas_nao_conciliadas_custeio': 0,
                    'receitas_nao_conciliadas_livre': 0,
                    'receitas_no_periodo': 100.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 100.0,
                    'repasses_no_periodo_capital': 0,
                    'repasses_no_periodo_custeio': 100.0,
                    'repasses_no_periodo_livre': 0,
                    'saldo_atual_capital': 1000.0,
                    'saldo_atual_custeio': 20.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 1020.0,
                    'saldo_bancario_capital': 1000.0,
                    'saldo_bancario_custeio': 70.0,
                    'saldo_bancario_livre': 0,
                    'saldo_bancario_total': 1070.0,
                },
            ],
            'totais': totais_esperados,
        }
    ]

    resultado_esperado = {
        'uuid': None,
        'contas': info_contas_esperadas,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou as informações esperadas."
