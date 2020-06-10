import json
from decimal import Decimal

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_tabela_valores_pendentes(jwt_authenticated_client, associacao, periodo, acao_associacao, tipo_receita, receita_100_no_periodo, prestacao_conta_iniciada):
    response = jwt_authenticated_client.get(f'/api/prestacoes-contas/tabela-valores-pendentes/?periodo={periodo.uuid}', content_type='application/json')
    result = json.loads(response.content)
    print(result)
    print(response.data)
    print(periodo.uuid)

    esperado = [
        {
            'acao_associacao_uuid': str(acao_associacao.uuid), 
            'acao_associacao_nome': 'PTRF', 
            'saldo_reprogramado': 0, 
            'saldo_reprogramado_capital': 0, 
            'saldo_reprogramado_custeio': 0, 
            'receitas_no_periodo': Decimal('100.00'), 
            'repasses_no_periodo': 0, 
            'repasses_no_periodo_capital': 0, 
            'repasses_no_periodo_custeio': 0, 
            'outras_receitas_no_periodo': Decimal('100.00'), 
            'outras_receitas_no_periodo_capital': 0, 
            'outras_receitas_no_periodo_custeio': Decimal('100.00'), 
            'despesas_no_periodo': 0, 
            'despesas_no_periodo_capital': 0, 
            'despesas_no_periodo_custeio': 0, 
            'despesas_nao_conciliadas': 0, 
            'despesas_nao_conciliadas_capital': 0, 
            'despesas_nao_conciliadas_custeio': 0, 
            'receitas_nao_conciliadas': Decimal('100.00'), 
            'receitas_nao_conciliadas_capital': 0, 
            'receitas_nao_conciliadas_custeio': Decimal('100.00'), 
            'saldo_atual_custeio': Decimal('100.00'), 
            'saldo_atual_capital': 0, 
            'saldo_atual_total': Decimal('100.00'), 
            'especificacoes_despesas_capital': [], 
            'especificacoes_despesas_custeio': []}]

    assert result == esperado