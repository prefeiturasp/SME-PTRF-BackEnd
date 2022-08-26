import pytest

from decimal import Decimal
from freezegun import freeze_time

from sme_ptrf_apps.core.services.painel_resumo_recursos_service import PainelResumoRecursosService

pytestmark = pytest.mark.django_db


@freeze_time('2020-01-01 10:20:00')
def test_painel_resumo_recursos_retorna_info_conta(
    prr_associacao,
    prr_periodo_2020_1,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
):
    status_pc_esperado = {
        'documentos_gerados': None,
        'legenda_cor': 1,
        'periodo_bloqueado': False,
        'periodo_encerrado': False,
        'prestacao_de_contas_uuid': None,
        'status_prestacao': 'NAO_APRESENTADA',
        'texto_status': 'Período em andamento. ',
        'requer_retificacao': False,
    }

    info_conta_esperada = {
        'conta_associacao_uuid': prr_conta_associacao_cheque.uuid,
        'conta_associacao_nome': prr_conta_associacao_cheque.tipo_conta.nome,

        'saldo_reprogramado': Decimal(0.00),
        'saldo_reprogramado_capital': Decimal(0.00),
        'saldo_reprogramado_custeio': Decimal(0.00),
        'saldo_reprogramado_livre': Decimal(0.00),

        'receitas_no_periodo': Decimal(0.00),

        'repasses_no_periodo': Decimal(0.00),
        'repasses_no_periodo_capital': Decimal(0.00),
        'repasses_no_periodo_custeio': Decimal(0.00),
        'repasses_no_periodo_livre': Decimal(0.00),

        'outras_receitas_no_periodo': Decimal(0.00),
        'outras_receitas_no_periodo_capital': Decimal(0.00),
        'outras_receitas_no_periodo_custeio': Decimal(0.00),
        'outras_receitas_no_periodo_livre': Decimal(0.00),

        'despesas_no_periodo': Decimal(0.00),
        'despesas_no_periodo_capital': Decimal(0.00),
        'despesas_no_periodo_custeio': Decimal(0.00),

        'saldo_atual_custeio': Decimal(0.00),
        'saldo_atual_capital': Decimal(0.00),
        'saldo_atual_livre': Decimal(0.00),
        'saldo_atual_total': Decimal(0.00)
    }

    info_acoes_esperado = [{
        'acao_associacao_uuid': prr_acao_associacao_ptrf.uuid,
        'acao_associacao_nome': prr_acao_associacao_ptrf.acao.nome,

        'saldo_reprogramado': Decimal(0.00),
        'saldo_reprogramado_capital': Decimal(0.00),
        'saldo_reprogramado_custeio': Decimal(0.00),
        'saldo_reprogramado_livre': Decimal(0.00),

        'receitas_no_periodo': Decimal(0.00),


        'repasses_no_periodo': Decimal(0.00),
        'repasses_no_periodo_capital': Decimal(0.00),
        'repasses_no_periodo_custeio': Decimal(0.00),
        'repasses_no_periodo_livre': Decimal(0.00),

        'outras_receitas_no_periodo': Decimal(0.00),

        'outras_receitas_no_periodo_capital': Decimal(0.00),

        'outras_receitas_no_periodo_custeio': Decimal(0.00),

        'outras_receitas_no_periodo_livre': Decimal(0.00),

        'despesas_no_periodo': Decimal(0.00),
        'despesas_no_periodo_capital': Decimal(0.00),
        'despesas_no_periodo_custeio': Decimal(0.00),

        'saldo_atual_custeio': Decimal(0.00),
        'saldo_atual_capital': Decimal(0.00),
        'saldo_atual_livre': Decimal(0.00),
        'saldo_atual_total': Decimal(0.00),

    }, ]

    json_esperado = {
        'associacao': prr_associacao.uuid,
        'periodo_referencia': prr_periodo_2020_1.referencia,
        'prestacao_contas_status': status_pc_esperado,
        'data_inicio_realizacao_despesas': f'{prr_periodo_2020_1.data_inicio_realizacao_despesas if prr_periodo_2020_1 else ""}',
        'data_fim_realizacao_despesas': f'{prr_periodo_2020_1.data_fim_realizacao_despesas if prr_periodo_2020_1 else ""}',
        'data_prevista_repasse': f'{prr_periodo_2020_1.data_prevista_repasse if prr_periodo_2020_1 else ""}',
        'ultima_atualizacao': '2020-01-01 10:20:00',
        'info_acoes': info_acoes_esperado,
        'info_conta': info_conta_esperada
    }

    painel = PainelResumoRecursosService.painel_resumo_recursos(
        prr_associacao,
        prr_periodo_2020_1,
        prr_conta_associacao_cheque
    )

    painel_em_json = painel.to_json()

    assert painel_em_json == json_esperado
