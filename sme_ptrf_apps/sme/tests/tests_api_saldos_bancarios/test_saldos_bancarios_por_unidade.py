import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db

cenario_1 = [
        {'tipo_de_unidade': 'IFSP', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CMCT', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CECI', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CEI', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CEMEI', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CIEJA', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'EMEBS', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'EMEF', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'EMEFM', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'EMEI', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CEU', 'qtde_unidades_informadas': 1, 'saldo_bancario_informado': 1000, 'total_unidades': 2},
        {'tipo_de_unidade': 'CEU CEI', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CEU EMEF', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CEU EMEI', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CEU CEMEI', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
        {'tipo_de_unidade': 'CEI DIRET', 'qtde_unidades_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 0},
    ]

def test_saldo_bancario_por_tipo_de_unidade(jwt_authenticated_client_sme, observacao_conciliacao_saldos_bancarios,
                                            periodo_saldos_bancarios,
                                            tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-tipo-unidade/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = cenario_1

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_saldo_bancario_por_tipo_de_unidade_com_conta_nao_iniciada(
    jwt_authenticated_client_sme,
    observacao_conciliacao_saldos_bancarios,
    observacao_conciliacao_saldos_bancarios_com_conta_nao_iniciada,
    periodo_saldos_bancarios,
    tipo_conta_saldos_bancarios
):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-tipo-unidade/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = cenario_1

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_saldo_bancario_por_tipo_de_unidade_com_conta_encerrada(
    jwt_authenticated_client_sme,
    observacao_conciliacao_saldos_bancarios,
    observacao_conciliacao_saldos_bancarios_com_conta_encerrada,
    solicitacao_encerramento_conta_aprovada,
    periodo_saldos_bancarios,
    tipo_conta_saldos_bancarios
):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-tipo-unidade/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = cenario_1

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_saldo_bancario_por_tipo_de_unidade_falta_periodo(jwt_authenticated_client_sme, tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-tipo-unidade/?conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-tipo-unidade',
        'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_saldo_bancario_por_tipo_de_unidade_falta_conta(jwt_authenticated_client_sme, periodo_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-tipo-unidade/?periodo={periodo_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-tipo-unidade',
        'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
