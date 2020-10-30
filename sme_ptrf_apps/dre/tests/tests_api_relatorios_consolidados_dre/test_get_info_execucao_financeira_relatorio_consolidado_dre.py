import json
import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_info_execucao_financeira_relatorio(jwt_authenticated_client, dre, periodo, tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-execucao-financeira/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'saldo_reprogramado_periodo_anterior_custeio': 0,
        'saldo_reprogramado_periodo_anterior_capital': 0,
        'saldo_reprogramado_periodo_anterior_livre': 0,
        'saldo_reprogramado_periodo_anterior_total': 0,

        'repasses_previstos_sme_custeio': 0,
        'repasses_previstos_sme_capital': 0,
        'repasses_previstos_sme_livre': 0,
        'repasses_previstos_sme_total': 0,

        'repasses_no_periodo_custeio': 0,
        'repasses_no_periodo_capital': 0,
        'repasses_no_periodo_livre': 0,
        'repasses_no_periodo_total': 0,

        'receitas_rendimento_no_periodo_custeio': 0,
        'receitas_rendimento_no_periodo_capital': 0,
        'receitas_rendimento_no_periodo_livre': 0,
        'receitas_rendimento_no_periodo_total': 0,

        'receitas_devolucao_no_periodo_custeio': 0,
        'receitas_devolucao_no_periodo_capital': 0,
        'receitas_devolucao_no_periodo_livre': 0,
        'receitas_devolucao_no_periodo_total': 0,

        'demais_creditos_no_periodo_custeio': 0,
        'demais_creditos_no_periodo_capital': 0,
        'demais_creditos_no_periodo_livre': 0,
        'demais_creditos_no_periodo_total': 0,

        'receitas_totais_no_periodo_custeio': 0,
        'receitas_totais_no_periodo_capital': 0,
        'receitas_totais_no_periodo_livre': 0,
        'receitas_totais_no_periodo_total': 0,

        'despesas_no_periodo_custeio': 0,
        'despesas_no_periodo_capital': 0,
        'despesas_no_periodo_total': 0,

        'saldo_reprogramado_proximo_periodo_custeio': 0,
        'saldo_reprogramado_proximo_periodo_capital': 0,
        'saldo_reprogramado_proximo_periodo_livre': 0,
        'saldo_reprogramado_proximo_periodo_total': 0,

        'devolucoes_ao_tesouro_no_periodo_total': 0,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_get_info_execucao_financeira_relatorio_sem_passa_dre(jwt_authenticated_client, dre, periodo, tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-execucao-financeira/?periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre',
        'operacao': 'info-execucao-financeira'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_execucao_financeira_relatorio_sem_passa_periodo(jwt_authenticated_client, dre, periodo,
                                                                      tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-execucao-financeira/?dre={dre.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo',
        'operacao': 'info-execucao-financeira'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_execucao_financeira_relatorio_sem_passar_tipo_conta(jwt_authenticated_client, dre, periodo,
                                                                          tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-execucao-financeira/?dre={dre.uuid}&periodo={periodo.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta',
        'operacao': 'info-execucao-financeira'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado
