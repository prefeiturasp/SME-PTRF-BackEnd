import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_info_para_ata(jwt_authenticated_client_a,
                               conta_associacao,
                               acao_associacao,
                               acao_associacao_role_cultural,
                               prestacao_conta_2020_1_conciliada,
                               fechamento_2020_1,
                               fechamento_2020_1_role,
                               fechamento_periodo_anterior_role
                               ):
    prestacao_uuid = prestacao_conta_2020_1_conciliada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/info-para-ata/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    totais_esperados = {
        'saldo_reprogramado': 300.0,
        'saldo_reprogramado_capital': 100.0,
        'saldo_reprogramado_custeio': 200.0,
        'saldo_reprogramado_livre': 0.0,

        'receitas_no_periodo': 6000.0,

        'receitas_devolucao_no_periodo': 0.0,
        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'repasses_no_periodo': 4500.0,
        'repasses_no_periodo_capital': 1900.0,
        'repasses_no_periodo_custeio': 2600.0,
        'repasses_no_periodo_livre': 0.0,

        'outras_receitas_no_periodo': 1500.0,
        'outras_receitas_no_periodo_capital': 1100.0,
        'outras_receitas_no_periodo_custeio': 400.0,
        'outras_receitas_no_periodo_livre': 0.0,

        'despesas_no_periodo': 2700.0,
        'despesas_no_periodo_capital': 1000.0,
        'despesas_no_periodo_custeio': 1700.0,
        'despesas_nao_conciliadas': 54.0,
        'despesas_nao_conciliadas_capital': 28.0,
        'despesas_nao_conciliadas_custeio': 26.0,

        'despesas_conciliadas': 2646.0,
        'despesas_conciliadas_capital': 972.0,
        'despesas_conciliadas_custeio': 1674.0,

        'despesas_nao_conciliadas_anteriores': 0,
        'despesas_nao_conciliadas_anteriores_capital': 0,
        'despesas_nao_conciliadas_anteriores_custeio': 0,

        'saldo_bancario_capital': 2128.0,
        'saldo_bancario_custeio': 1526.0,
        'saldo_bancario_livre': 0.0,
        'saldo_bancario_total': 3654.0,

        'receitas_nao_conciliadas': 60.0,
        'receitas_nao_conciliadas_capital': 30.0,
        'receitas_nao_conciliadas_custeio': 30.0,
        'receitas_nao_conciliadas_livre': 0.0,

        'saldo_atual_capital': 2100.0,
        'saldo_atual_custeio': 1500.0,
        'saldo_atual_livre': 0.0,
        'saldo_atual_total': 3600.0,

        'repasses_nao_realizados_capital': 0,
        'repasses_nao_realizados_custeio': 0,
        'repasses_nao_realizados_livre': 0
    }

    info_contas_esperadas = [
        {

            'conta_associacao': {'agencia': '12345',
                                 'banco_nome': 'Banco do Brasil',
                                 'nome': 'Cheque',
                                 'numero_conta': '123456-x',
                                 'uuid': f'{conta_associacao.uuid}'},
            'acoes': [
                {
                    'acao_associacao_nome': 'PTRF',
                    'acao_associacao_uuid': f'{acao_associacao.uuid}',
                    'despesas_nao_conciliadas': 24.0,
                    'despesas_nao_conciliadas_capital': 8.0,
                    'despesas_nao_conciliadas_custeio': 16.0,
                    'despesas_conciliadas': 2376.0,
                    'despesas_conciliadas_capital': 792.0,
                    'despesas_conciliadas_custeio': 1584.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 208.0,
                    'saldo_bancario_custeio': 416.0,
                    'saldo_bancario_livre': 0.0,
                    'saldo_bancario_total': 624.0,
                    'despesas_no_periodo': 2400.0,
                    'despesas_no_periodo_capital': 800.0,
                    'despesas_no_periodo_custeio': 1600.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['cadeira', 'mesa'],
                    'outras_receitas_no_periodo': 300.0,
                    'outras_receitas_no_periodo_capital': 100.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 0.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 30.0,
                    'receitas_nao_conciliadas_capital': 10.0,
                    'receitas_nao_conciliadas_custeio': 20.0,
                    'receitas_nao_conciliadas_livre': 0.0,
                    'receitas_no_periodo': 3000.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 2700.0,
                    'repasses_no_periodo_capital': 900.0,
                    'repasses_no_periodo_custeio': 1800.0,
                    'repasses_no_periodo_livre': 0.0,
                    'saldo_atual_capital': 200.0,
                    'saldo_atual_custeio': 400.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 600.0,
                    'saldo_reprogramado': 0,
                    'saldo_reprogramado_capital': 0,
                    'saldo_reprogramado_custeio': 0,
                    'saldo_reprogramado_livre': 0
                },
                {
                    'acao_associacao_nome': 'Rolê Cultural',
                    'acao_associacao_uuid': f'{acao_associacao_role_cultural.uuid}',
                    'despesas_nao_conciliadas': 30.0,
                    'despesas_nao_conciliadas_capital': 20.0,
                    'despesas_nao_conciliadas_custeio': 10.0,
                    'despesas_conciliadas': 270.0,
                    'despesas_conciliadas_capital': 180.0,
                    'despesas_conciliadas_custeio': 90.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 1920.0,
                    'saldo_bancario_custeio': 1110.0,
                    'saldo_bancario_livre': 0.0,
                    'saldo_bancario_total': 3030.0,
                    'despesas_no_periodo': 300.0,
                    'despesas_no_periodo_capital': 200.0,
                    'despesas_no_periodo_custeio': 100.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['ventilador',
                                                        'contador'],
                    'outras_receitas_no_periodo': 1200.0,
                    'outras_receitas_no_periodo_capital': 1000.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 0.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 30.0,
                    'receitas_nao_conciliadas_capital': 20.0,
                    'receitas_nao_conciliadas_custeio': 10.0,
                    'receitas_nao_conciliadas_livre': 0.0,
                    'receitas_no_periodo': 3000.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 1800.0,
                    'repasses_no_periodo_capital': 1000.0,
                    'repasses_no_periodo_custeio': 800.0,
                    'repasses_no_periodo_livre': 0.0,
                    'saldo_atual_capital': 1900.0,
                    'saldo_atual_custeio': 1100.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 3000.0,
                    'saldo_reprogramado': 300.0,
                    'saldo_reprogramado_capital': 100.0,
                    'saldo_reprogramado_custeio': 200.0,
                    'saldo_reprogramado_livre': 0.0
                }
            ],
            'totais': totais_esperados,
        }
    ]

    resultado_esperado = {
        'uuid': f'{prestacao_uuid}',
        'contas': info_contas_esperadas,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou as informações esperadas."


def test_api_get_info_para_ata_com_repasses_pendentes(jwt_authenticated_client_a,
                                                      conta_associacao,
                                                      acao_associacao,
                                                      acao_associacao_role_cultural,
                                                      prestacao_conta_2020_1_conciliada,
                                                      fechamento_2020_1,
                                                      fechamento_2020_1_role,
                                                      fechamento_periodo_anterior_role,
                                                      repasse_2020_1_pendente,
                                                      ):
    prestacao_uuid = prestacao_conta_2020_1_conciliada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/info-para-ata/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)
    totais_esperados = {
        'saldo_reprogramado': 300.0,
        'saldo_reprogramado_capital': 100.0,
        'saldo_reprogramado_custeio': 200.0,
        'saldo_reprogramado_livre': 0.0,

        'receitas_no_periodo': 6000.0,

        'receitas_devolucao_no_periodo': 0.0,
        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'repasses_no_periodo': 4500.0,
        'repasses_no_periodo_capital': 1900.0,
        'repasses_no_periodo_custeio': 2600.0,
        'repasses_no_periodo_livre': 0.0,

        'outras_receitas_no_periodo': 1500.0,
        'outras_receitas_no_periodo_capital': 1100.0,
        'outras_receitas_no_periodo_custeio': 400.0,
        'outras_receitas_no_periodo_livre': 0.0,

        'despesas_no_periodo': 2700.0,
        'despesas_no_periodo_capital': 1000.0,
        'despesas_no_periodo_custeio': 1700.0,
        'despesas_nao_conciliadas': 54.0,
        'despesas_nao_conciliadas_capital': 28.0,
        'despesas_nao_conciliadas_custeio': 26.0,

        'despesas_conciliadas': 2646.0,
        'despesas_conciliadas_capital': 972.0,
        'despesas_conciliadas_custeio': 1674.0,

        'despesas_nao_conciliadas_anteriores': 0,
        'despesas_nao_conciliadas_anteriores_capital': 0,
        'despesas_nao_conciliadas_anteriores_custeio': 0,

        'saldo_bancario_capital': 2128.0,
        'saldo_bancario_custeio': 1526.0,
        'saldo_bancario_livre': 0.0,
        'saldo_bancario_total': 3654.0,

        'receitas_nao_conciliadas': 60.0,
        'receitas_nao_conciliadas_capital': 30.0,
        'receitas_nao_conciliadas_custeio': 30.0,
        'receitas_nao_conciliadas_livre': 0.0,

        'saldo_atual_capital': 2100.0,
        'saldo_atual_custeio': 1500.0,
        'saldo_atual_livre': 0.0,
        'saldo_atual_total': 3600.0,

        'repasses_nao_realizados_capital': 1000.0,
        'repasses_nao_realizados_custeio': 1000.0,
        'repasses_nao_realizados_livre': 0
    }

    info_contas_esperadas = [
        {
            'conta_associacao': {'agencia': '12345',
                                 'banco_nome': 'Banco do Brasil',
                                 'nome': 'Cheque',
                                 'numero_conta': '123456-x',
                                 'uuid': f'{conta_associacao.uuid}'},
            'acoes': [
                {
                    'acao_associacao_nome': 'PTRF',
                    'acao_associacao_uuid': f'{acao_associacao.uuid}',
                    'despesas_nao_conciliadas': 24.0,
                    'despesas_nao_conciliadas_capital': 8.0,
                    'despesas_nao_conciliadas_custeio': 16.0,
                    'despesas_conciliadas': 2376.0,
                    'despesas_conciliadas_capital': 792.0,
                    'despesas_conciliadas_custeio': 1584.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 208.0,
                    'saldo_bancario_custeio': 416.0,
                    'saldo_bancario_livre': 0.0,
                    'saldo_bancario_total': 624.0,
                    'despesas_no_periodo': 2400.0,
                    'despesas_no_periodo_capital': 800.0,
                    'despesas_no_periodo_custeio': 1600.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['cadeira', 'mesa'],
                    'outras_receitas_no_periodo': 300.0,
                    'outras_receitas_no_periodo_capital': 100.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 0.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 30.0,
                    'receitas_nao_conciliadas_capital': 10.0,
                    'receitas_nao_conciliadas_custeio': 20.0,
                    'receitas_nao_conciliadas_livre': 0.0,
                    'receitas_no_periodo': 3000.0,
                    'repasses_nao_realizados_capital': 1000.0,
                    'repasses_nao_realizados_custeio': 1000.0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 2700.0,
                    'repasses_no_periodo_capital': 900.0,
                    'repasses_no_periodo_custeio': 1800.0,
                    'repasses_no_periodo_livre': 0.0,
                    'saldo_atual_capital': 200.0,
                    'saldo_atual_custeio': 400.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 600.0,
                    'saldo_reprogramado': 0,
                    'saldo_reprogramado_capital': 0,
                    'saldo_reprogramado_custeio': 0,
                    'saldo_reprogramado_livre': 0
                },
                {
                    'acao_associacao_nome': 'Rolê Cultural',
                    'acao_associacao_uuid': f'{acao_associacao_role_cultural.uuid}',
                    'despesas_nao_conciliadas': 30.0,
                    'despesas_nao_conciliadas_capital': 20.0,
                    'despesas_nao_conciliadas_custeio': 10.0,
                    'despesas_conciliadas': 270.0,
                    'despesas_conciliadas_capital': 180.0,
                    'despesas_conciliadas_custeio': 90.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 1920.0,
                    'saldo_bancario_custeio': 1110.0,
                    'saldo_bancario_livre': 0.0,
                    'saldo_bancario_total': 3030.0,
                    'despesas_no_periodo': 300.0,
                    'despesas_no_periodo_capital': 200.0,
                    'despesas_no_periodo_custeio': 100.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['ventilador',
                                                        'contador'],
                    'outras_receitas_no_periodo': 1200.0,
                    'outras_receitas_no_periodo_capital': 1000.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 0.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 30.0,
                    'receitas_nao_conciliadas_capital': 20.0,
                    'receitas_nao_conciliadas_custeio': 10.0,
                    'receitas_nao_conciliadas_livre': 0.0,
                    'receitas_no_periodo': 3000.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 1800.0,
                    'repasses_no_periodo_capital': 1000.0,
                    'repasses_no_periodo_custeio': 800.0,
                    'repasses_no_periodo_livre': 0.0,
                    'saldo_atual_capital': 1900.0,
                    'saldo_atual_custeio': 1100.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 3000.0,
                    'saldo_reprogramado': 300.0,
                    'saldo_reprogramado_capital': 100.0,
                    'saldo_reprogramado_custeio': 200.0,
                    'saldo_reprogramado_livre': 0.0
                }
            ],
            'totais': totais_esperados,
        }
    ]

    resultado_esperado = {
        'uuid': f'{prestacao_uuid}',
        'contas': info_contas_esperadas,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou as informações esperadas."


def test_api_get_info_para_ata_com_repasses_pendentes_custeio(jwt_authenticated_client_a,
                                                              conta_associacao,
                                                              acao_associacao,
                                                              acao_associacao_role_cultural,
                                                              prestacao_conta_2020_1_conciliada,
                                                              fechamento_2020_1,
                                                              fechamento_2020_1_role,
                                                              fechamento_periodo_anterior_role,
                                                              repasse_2020_1_custeio_pendente,
                                                              repasse_2019_2_pendente,
                                                              ):
    prestacao_uuid = prestacao_conta_2020_1_conciliada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/info-para-ata/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    totais_esperados = {
        'saldo_reprogramado': 300.0,
        'saldo_reprogramado_capital': 100.0,
        'saldo_reprogramado_custeio': 200.0,
        'saldo_reprogramado_livre': 0.0,

        'receitas_no_periodo': 6000.0,

        'receitas_devolucao_no_periodo': 0.0,
        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'repasses_no_periodo': 4500.0,
        'repasses_no_periodo_capital': 1900.0,
        'repasses_no_periodo_custeio': 2600.0,
        'repasses_no_periodo_livre': 0.0,

        'outras_receitas_no_periodo': 1500.0,
        'outras_receitas_no_periodo_capital': 1100.0,
        'outras_receitas_no_periodo_custeio': 400.0,
        'outras_receitas_no_periodo_livre': 0.0,

        'despesas_no_periodo': 2700.0,
        'despesas_no_periodo_capital': 1000.0,
        'despesas_no_periodo_custeio': 1700.0,
        'despesas_nao_conciliadas': 54.0,
        'despesas_nao_conciliadas_capital': 28.0,
        'despesas_nao_conciliadas_custeio': 26.0,

        'despesas_conciliadas': 2646.0,
        'despesas_conciliadas_capital': 972.0,
        'despesas_conciliadas_custeio': 1674.0,

        'despesas_nao_conciliadas_anteriores': 0,
        'despesas_nao_conciliadas_anteriores_capital': 0,
        'despesas_nao_conciliadas_anteriores_custeio': 0,

        'saldo_bancario_capital': 2128.0,
        'saldo_bancario_custeio': 1526.0,
        'saldo_bancario_livre': 0.0,
        'saldo_bancario_total': 3654.0,

        'receitas_nao_conciliadas': 60.0,
        'receitas_nao_conciliadas_capital': 30.0,
        'receitas_nao_conciliadas_custeio': 30.0,
        'receitas_nao_conciliadas_livre': 0.0,

        'saldo_atual_capital': 2100.0,
        'saldo_atual_custeio': 1500.0,
        'saldo_atual_livre': 0.0,
        'saldo_atual_total': 3600.0,

        'repasses_nao_realizados_capital': 0,
        'repasses_nao_realizados_custeio': 1000.0,
        'repasses_nao_realizados_livre': 0
    }

    info_contas_esperadas = [
        {
            'conta_associacao': {'agencia': '12345',
                                 'banco_nome': 'Banco do Brasil',
                                 'nome': 'Cheque',
                                 'numero_conta': '123456-x',
                                 'uuid': f'{conta_associacao.uuid}'},
            'acoes': [
                {
                    'acao_associacao_nome': 'PTRF',
                    'acao_associacao_uuid': f'{acao_associacao.uuid}',
                    'despesas_nao_conciliadas': 24.0,
                    'despesas_nao_conciliadas_capital': 8.0,
                    'despesas_nao_conciliadas_custeio': 16.0,
                    'despesas_conciliadas': 2376.0,
                    'despesas_conciliadas_capital': 792.0,
                    'despesas_conciliadas_custeio': 1584.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 208.0,
                    'saldo_bancario_custeio': 416.0,
                    'saldo_bancario_livre': 0.0,
                    'saldo_bancario_total': 624.0,
                    'despesas_no_periodo': 2400.0,
                    'despesas_no_periodo_capital': 800.0,
                    'despesas_no_periodo_custeio': 1600.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['cadeira', 'mesa'],
                    'outras_receitas_no_periodo': 300.0,
                    'outras_receitas_no_periodo_capital': 100.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 0.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 30.0,
                    'receitas_nao_conciliadas_capital': 10.0,
                    'receitas_nao_conciliadas_custeio': 20.0,
                    'receitas_nao_conciliadas_livre': 0.0,
                    'receitas_no_periodo': 3000.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 1000.0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 2700.0,
                    'repasses_no_periodo_capital': 900.0,
                    'repasses_no_periodo_custeio': 1800.0,
                    'repasses_no_periodo_livre': 0.0,
                    'saldo_atual_capital': 200.0,
                    'saldo_atual_custeio': 400.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 600.0,
                    'saldo_reprogramado': 0,
                    'saldo_reprogramado_capital': 0,
                    'saldo_reprogramado_custeio': 0,
                    'saldo_reprogramado_livre': 0
                },
                {
                    'acao_associacao_nome': 'Rolê Cultural',
                    'acao_associacao_uuid': f'{acao_associacao_role_cultural.uuid}',
                    'despesas_nao_conciliadas': 30.0,
                    'despesas_nao_conciliadas_capital': 20.0,
                    'despesas_nao_conciliadas_custeio': 10.0,
                    'despesas_conciliadas': 270.0,
                    'despesas_conciliadas_capital': 180.0,
                    'despesas_conciliadas_custeio': 90.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 1920.0,
                    'saldo_bancario_custeio': 1110.0,
                    'saldo_bancario_livre': 0.0,
                    'saldo_bancario_total': 3030.0,
                    'despesas_no_periodo': 300.0,
                    'despesas_no_periodo_capital': 200.0,
                    'despesas_no_periodo_custeio': 100.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['ventilador',
                                                        'contador'],
                    'outras_receitas_no_periodo': 1200.0,
                    'outras_receitas_no_periodo_capital': 1000.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 0.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 30.0,
                    'receitas_nao_conciliadas_capital': 20.0,
                    'receitas_nao_conciliadas_custeio': 10.0,
                    'receitas_nao_conciliadas_livre': 0.0,
                    'receitas_no_periodo': 3000.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 1800.0,
                    'repasses_no_periodo_capital': 1000.0,
                    'repasses_no_periodo_custeio': 800.0,
                    'repasses_no_periodo_livre': 0.0,
                    'saldo_atual_capital': 1900.0,
                    'saldo_atual_custeio': 1100.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 3000.0,
                    'saldo_reprogramado': 300.0,
                    'saldo_reprogramado_capital': 100.0,
                    'saldo_reprogramado_custeio': 200.0,
                    'saldo_reprogramado_livre': 0.0
                }
            ],
            'totais': totais_esperados,
        }
    ]

    resultado_esperado = {
        'uuid': f'{prestacao_uuid}',
        'contas': info_contas_esperadas,
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou as informações esperadas."


def test_api_get_info_para_ata_com_livre_aplicacao(jwt_authenticated_client_a,
                                                   conta_associacao,
                                                   acao_associacao,
                                                   acao_associacao_role_cultural,
                                                   prestacao_conta_2020_1_conciliada,
                                                   fechamento_2020_1_com_livre,
                                                   fechamento_2020_1_role,
                                                   fechamento_periodo_anterior_role,
                                                   ):
    prestacao_uuid = prestacao_conta_2020_1_conciliada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/info-para-ata/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    totais_esperados = {
        'saldo_reprogramado': 300.0,
        'saldo_reprogramado_capital': 100.0,
        'saldo_reprogramado_custeio': 200.0,
        'saldo_reprogramado_livre': 0.0,

        'receitas_no_periodo': 9000.0,

        'receitas_devolucao_no_periodo': 0.0,
        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'repasses_no_periodo': 7200.0,
        'repasses_no_periodo_capital': 1900.0,
        'repasses_no_periodo_custeio': 2600.0,
        'repasses_no_periodo_livre': 2700.0,

        'outras_receitas_no_periodo': 1800.0,
        'outras_receitas_no_periodo_capital': 1100.0,
        'outras_receitas_no_periodo_custeio': 400.0,
        'outras_receitas_no_periodo_livre': 300.0,

        'despesas_no_periodo': 2700.0,
        'despesas_no_periodo_capital': 1000.0,
        'despesas_no_periodo_custeio': 1700.0,
        'despesas_nao_conciliadas': 54.0,
        'despesas_nao_conciliadas_capital': 28.0,
        'despesas_nao_conciliadas_custeio': 26.0,

        'despesas_conciliadas': 2646.0,
        'despesas_conciliadas_capital': 972.0,
        'despesas_conciliadas_custeio': 1674.0,

        'despesas_nao_conciliadas_anteriores': 0,
        'despesas_nao_conciliadas_anteriores_capital': 0,
        'despesas_nao_conciliadas_anteriores_custeio': 0,

        'saldo_bancario_capital': 2128.0,
        'saldo_bancario_custeio': 1526.0,
        'saldo_bancario_livre': 3000.0,
        'saldo_bancario_total': 6654.0,

        'receitas_nao_conciliadas': 90.0,
        'receitas_nao_conciliadas_capital': 30.0,
        'receitas_nao_conciliadas_custeio': 30.0,
        'receitas_nao_conciliadas_livre': 30.0,

        'saldo_atual_capital': 2100.0,
        'saldo_atual_custeio': 1500.0,
        'saldo_atual_livre': 3000.0,
        'saldo_atual_total': 6600.0,

        'repasses_nao_realizados_capital': 0,
        'repasses_nao_realizados_custeio': 0,
        'repasses_nao_realizados_livre': 0
    }

    info_contas_esperadas = [
        {
            'conta_associacao': {'agencia': '12345',
                                 'banco_nome': 'Banco do Brasil',
                                 'nome': 'Cheque',
                                 'numero_conta': '123456-x',
                                 'uuid': f'{conta_associacao.uuid}'},
            'acoes': [
                {
                    'acao_associacao_nome': 'PTRF',
                    'acao_associacao_uuid': f'{acao_associacao.uuid}',
                    'despesas_nao_conciliadas': 24.0,
                    'despesas_nao_conciliadas_capital': 8.0,
                    'despesas_nao_conciliadas_custeio': 16.0,
                    'despesas_conciliadas': 2376.0,
                    'despesas_conciliadas_capital': 792.0,
                    'despesas_conciliadas_custeio': 1584.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 208.0,
                    'saldo_bancario_custeio': 416.0,
                    'saldo_bancario_livre': 3000.0,
                    'saldo_bancario_total': 3624.0,
                    'despesas_no_periodo': 2400.0,
                    'despesas_no_periodo_capital': 800.0,
                    'despesas_no_periodo_custeio': 1600.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['cadeira', 'mesa'],
                    'outras_receitas_no_periodo': 600.0,
                    'outras_receitas_no_periodo_capital': 100.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 300.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 60.0,
                    'receitas_nao_conciliadas_capital': 10.0,
                    'receitas_nao_conciliadas_custeio': 20.0,
                    'receitas_nao_conciliadas_livre': 30.0,
                    'receitas_no_periodo': 6000.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 5400.0,
                    'repasses_no_periodo_capital': 900.0,
                    'repasses_no_periodo_custeio': 1800.0,
                    'repasses_no_periodo_livre': 2700.0,
                    'saldo_atual_capital': 200.0,
                    'saldo_atual_custeio': 400.0,
                    'saldo_atual_livre': 3000.0,
                    'saldo_atual_total': 3600.0,
                    'saldo_reprogramado': 0,
                    'saldo_reprogramado_capital': 0,
                    'saldo_reprogramado_custeio': 0,
                    'saldo_reprogramado_livre': 0
                },
                {
                    'acao_associacao_nome': 'Rolê Cultural',
                    'acao_associacao_uuid': f'{acao_associacao_role_cultural.uuid}',
                    'despesas_nao_conciliadas': 30.0,
                    'despesas_nao_conciliadas_capital': 20.0,
                    'despesas_nao_conciliadas_custeio': 10.0,
                    'despesas_conciliadas': 270.0,
                    'despesas_conciliadas_capital': 180.0,
                    'despesas_conciliadas_custeio': 90.0,
                    'despesas_nao_conciliadas_anteriores': 0,
                    'despesas_nao_conciliadas_anteriores_capital': 0,
                    'despesas_nao_conciliadas_anteriores_custeio': 0,
                    'saldo_bancario_capital': 1920.0,
                    'saldo_bancario_custeio': 1110.0,
                    'saldo_bancario_livre': 0.0,
                    'saldo_bancario_total': 3030.0,
                    'despesas_no_periodo': 300.0,
                    'despesas_no_periodo_capital': 200.0,
                    'despesas_no_periodo_custeio': 100.0,
                    'especificacoes_despesas_capital': ['ar condicionado'],
                    'especificacoes_despesas_custeio': ['ventilador',
                                                        'contador'],
                    'outras_receitas_no_periodo': 1200.0,
                    'outras_receitas_no_periodo_capital': 1000.0,
                    'outras_receitas_no_periodo_custeio': 200.0,
                    'outras_receitas_no_periodo_livre': 0.0,
                    'receitas_devolucao_no_periodo': 0.0,
                    'receitas_devolucao_no_periodo_capital': 0.0,
                    'receitas_devolucao_no_periodo_custeio': 0.0,
                    'receitas_devolucao_no_periodo_livre': 0.0,
                    'receitas_nao_conciliadas': 30.0,
                    'receitas_nao_conciliadas_capital': 20.0,
                    'receitas_nao_conciliadas_custeio': 10.0,
                    'receitas_nao_conciliadas_livre': 0.0,
                    'receitas_no_periodo': 3000.0,
                    'repasses_nao_realizados_capital': 0,
                    'repasses_nao_realizados_custeio': 0,
                    'repasses_nao_realizados_livre': 0,
                    'repasses_no_periodo': 1800.0,
                    'repasses_no_periodo_capital': 1000.0,
                    'repasses_no_periodo_custeio': 800.0,
                    'repasses_no_periodo_livre': 0.0,
                    'saldo_atual_capital': 1900.0,
                    'saldo_atual_custeio': 1100.0,
                    'saldo_atual_livre': 0.0,
                    'saldo_atual_total': 3000.0,
                    'saldo_reprogramado': 300.0,
                    'saldo_reprogramado_capital': 100.0,
                    'saldo_reprogramado_custeio': 200.0,
                    'saldo_reprogramado_livre': 0.0
                }
            ],
            'totais': totais_esperados,
        }
    ]

    resultado_esperado = {
        'uuid': f'{prestacao_uuid}',
        'contas': info_contas_esperadas,
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou as informações esperadas."


def test_api_get_info_para_ata_com_duas_contas(jwt_authenticated_client_a,
                                               conta_associacao,
                                               conta_associacao_cartao,
                                               acao_associacao_role_cultural,
                                               prestacao_conta_2020_1_conciliada,
                                               fechamento_2020_1_role,
                                               fechamento_2020_1_role_cartao
                                               ):
    prestacao_uuid = prestacao_conta_2020_1_conciliada.uuid

    url = f'/api/prestacoes-contas/{prestacao_uuid}/info-para-ata/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    totais_esperados = {
        'despesas_nao_conciliadas': 30.0,
        'despesas_nao_conciliadas_capital': 20.0,
        'despesas_nao_conciliadas_custeio': 10.0,
        'despesas_conciliadas': 270.0,
        'despesas_conciliadas_capital': 180.0,
        'despesas_conciliadas_custeio': 90.0,
        'despesas_nao_conciliadas_anteriores': 0,
        'despesas_nao_conciliadas_anteriores_capital': 0,
        'despesas_nao_conciliadas_anteriores_custeio': 0,
        'saldo_bancario_capital': 1920.0,
        'saldo_bancario_custeio': 1110.0,
        'saldo_bancario_livre': 0.0,
        'saldo_bancario_total': 3030.0,
        'despesas_no_periodo': 300.0,
        'despesas_no_periodo_capital': 200.0,
        'despesas_no_periodo_custeio': 100.0,
        'outras_receitas_no_periodo': 1200.0,
        'outras_receitas_no_periodo_capital': 1000.0,
        'outras_receitas_no_periodo_custeio': 200.0,
        'outras_receitas_no_periodo_livre': 0.0,
        'receitas_devolucao_no_periodo': 0.0,
        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,
        'receitas_nao_conciliadas': 30.0,
        'receitas_nao_conciliadas_capital': 20.0,
        'receitas_nao_conciliadas_custeio': 10.0,
        'receitas_nao_conciliadas_livre': 0.0,
        'receitas_no_periodo': 3000.0,
        'repasses_nao_realizados_capital': 0,
        'repasses_nao_realizados_custeio': 0,
        'repasses_nao_realizados_livre': 0,
        'repasses_no_periodo': 1800.0,
        'repasses_no_periodo_capital': 1000.0,
        'repasses_no_periodo_custeio': 800.0,
        'repasses_no_periodo_livre': 0.0,
        'saldo_atual_capital': 1900.0,
        'saldo_atual_custeio': 1100.0,
        'saldo_atual_livre': 0.0,
        'saldo_atual_total': 3000.0,
        'saldo_reprogramado': 300.0,
        'saldo_reprogramado_capital': 100.0,
        'saldo_reprogramado_custeio': 200.0,
        'saldo_reprogramado_livre': 0.0
    }

    acoes_esperadas = [
        {
            'acao_associacao_nome': 'Rolê Cultural',
            'acao_associacao_uuid': f'{acao_associacao_role_cultural.uuid}',
            'despesas_nao_conciliadas': 30.0,
            'despesas_nao_conciliadas_capital': 20.0,
            'despesas_nao_conciliadas_custeio': 10.0,
            'despesas_conciliadas': 270.0,
            'despesas_conciliadas_capital': 180.0,
            'despesas_conciliadas_custeio': 90.0,
            'despesas_nao_conciliadas_anteriores': 0,
            'despesas_nao_conciliadas_anteriores_capital': 0,
            'despesas_nao_conciliadas_anteriores_custeio': 0,
            'saldo_bancario_capital': 1920.0,
            'saldo_bancario_custeio': 1110.0,
            'saldo_bancario_livre': 0.0,
            'saldo_bancario_total': 3030.0,
            'despesas_no_periodo': 300.0,
            'despesas_no_periodo_capital': 200.0,
            'despesas_no_periodo_custeio': 100.0,
            'especificacoes_despesas_capital': ['ar condicionado'],
            'especificacoes_despesas_custeio': ['ventilador',
                                                'contador'],
            'outras_receitas_no_periodo': 1200.0,
            'outras_receitas_no_periodo_capital': 1000.0,
            'outras_receitas_no_periodo_custeio': 200.0,
            'outras_receitas_no_periodo_livre': 0.0,
            'receitas_devolucao_no_periodo': 0.0,
            'receitas_devolucao_no_periodo_capital': 0.0,
            'receitas_devolucao_no_periodo_custeio': 0.0,
            'receitas_devolucao_no_periodo_livre': 0.0,
            'receitas_nao_conciliadas': 30.0,
            'receitas_nao_conciliadas_capital': 20.0,
            'receitas_nao_conciliadas_custeio': 10.0,
            'receitas_nao_conciliadas_livre': 0.0,
            'receitas_no_periodo': 3000.0,
            'repasses_nao_realizados_capital': 0,
            'repasses_nao_realizados_custeio': 0,
            'repasses_nao_realizados_livre': 0,
            'repasses_no_periodo': 1800.0,
            'repasses_no_periodo_capital': 1000.0,
            'repasses_no_periodo_custeio': 800.0,
            'repasses_no_periodo_livre': 0.0,
            'saldo_atual_capital': 1900.0,
            'saldo_atual_custeio': 1100.0,
            'saldo_atual_livre': 0.0,
            'saldo_atual_total': 3000.0,
            'saldo_reprogramado': 300.0,
            'saldo_reprogramado_capital': 100.0,
            'saldo_reprogramado_custeio': 200.0,
            'saldo_reprogramado_livre': 0.0
        }
    ]

    info_conta_cartao = {
        'conta_associacao': {'agencia': '',
                             'banco_nome': '',
                             'nome': 'Cartão',
                             'numero_conta': '',
                             'uuid': f'{conta_associacao_cartao.uuid}'},
        'acoes': acoes_esperadas,
        'totais': totais_esperados,
    }

    info_conta_cheque = {
        'conta_associacao': {'agencia': '12345',
                             'banco_nome': 'Banco do Brasil',
                             'nome': 'Cheque',
                             'numero_conta': '123456-x',
                             'uuid': f'{conta_associacao.uuid}'},

        'acoes':  acoes_esperadas,
        'totais': totais_esperados,
    }


    resultado_esperado_1 = {
        'uuid': f'{prestacao_uuid}',
        'contas': [info_conta_cartao, info_conta_cheque, ],
    }

    resultado_esperado_2 = {
        'uuid': f'{prestacao_uuid}',
        'contas': [info_conta_cheque, info_conta_cartao],
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado_1 or result == resultado_esperado_2, "Não retornou as informações esperadas."
