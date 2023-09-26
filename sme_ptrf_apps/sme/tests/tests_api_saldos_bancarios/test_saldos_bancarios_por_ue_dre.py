import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db

def get_payload_cenario_1(dre, dre_saldos_bancarios):
    return [{'associacoes': [{'associacao': 'IFSP', 'saldo_total': 0},
                                           {'associacao': 'CMCT', 'saldo_total': 0},
                                           {'associacao': 'CECI', 'saldo_total': 0},
                                           {'associacao': 'CEI', 'saldo_total': 0},
                                           {'associacao': 'CEMEI', 'saldo_total': 0},
                                           {'associacao': 'CIEJA', 'saldo_total': 0},
                                           {'associacao': 'EMEBS', 'saldo_total': 0},
                                           {'associacao': 'EMEF', 'saldo_total': 0},
                                           {'associacao': 'EMEFM', 'saldo_total': 0},
                                           {'associacao': 'EMEI', 'saldo_total': 0},
                                           {'associacao': 'CEU', 'saldo_total': 0},
                                           {'associacao': 'CEU CEI', 'saldo_total': 0},
                                           {'associacao': 'CEU EMEF', 'saldo_total': 0},
                                           {'associacao': 'CEU EMEI', 'saldo_total': 0},
                                           {'associacao': 'CEU CEMEI', 'saldo_total': 0},
                                           {'associacao': 'CEI DIRET', 'saldo_total': 0}
                                           ],
                           'nome_dre': 'DRE TESTE',
                           'sigla_dre': dre.sigla,
                           'uuid_dre': f'{dre.uuid}'},
                          {'associacoes': [{'associacao': 'IFSP', 'saldo_total': 0},
                                           {'associacao': 'CMCT', 'saldo_total': 0},
                                           {'associacao': 'CECI', 'saldo_total': 0},
                                           {'associacao': 'CEI', 'saldo_total': 0},
                                           {'associacao': 'CEMEI', 'saldo_total': 0},
                                           {'associacao': 'CIEJA', 'saldo_total': 0},
                                           {'associacao': 'EMEBS', 'saldo_total': 0},
                                           {'associacao': 'EMEF', 'saldo_total': 0},
                                           {'associacao': 'EMEFM', 'saldo_total': 0},
                                           {'associacao': 'EMEI', 'saldo_total': 0},
                                           {'associacao': 'CEU', 'saldo_total': 1000.0},
                                           {'associacao': 'CEU CEI', 'saldo_total': 0},
                                           {'associacao': 'CEU EMEF', 'saldo_total': 0},
                                           {'associacao': 'CEU EMEI', 'saldo_total': 0},
                                           {'associacao': 'CEU CEMEI', 'saldo_total': 0},
                                           {'associacao': 'CEI DIRET', 'saldo_total': 0}
                                           ],
                           'nome_dre': 'DRE TESTE2',
                           'sigla_dre': dre_saldos_bancarios.sigla,
                           'uuid_dre': f'{dre_saldos_bancarios.uuid}'}]

def test_saldo_bancario_por_ue_dre(jwt_authenticated_client_sme, observacao_conciliacao_saldos_bancarios,
                                   periodo_saldos_bancarios,
                                   tipo_conta_saldos_bancarios,
                                   dre,
                                   dre_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = get_payload_cenario_1(dre, dre_saldos_bancarios)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

def test_saldo_bancario_por_ue_dre_com_conta_nao_iniciada(
    jwt_authenticated_client_sme,
    observacao_conciliacao_saldos_bancarios,
    observacao_conciliacao_saldos_bancarios_com_conta_nao_iniciada,
    periodo_saldos_bancarios,
    tipo_conta_saldos_bancarios,
    dre,
    dre_saldos_bancarios
):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = get_payload_cenario_1(dre, dre_saldos_bancarios)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_saldo_bancario_por_ue_dre_com_conta_encerrada(
    jwt_authenticated_client_sme,
    observacao_conciliacao_saldos_bancarios,
    observacao_conciliacao_saldos_bancarios_com_conta_encerrada,
    solicitacao_encerramento_conta_aprovada,
    periodo_saldos_bancarios,
    tipo_conta_saldos_bancarios,
    dre,
    dre_saldos_bancarios
):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = get_payload_cenario_1(dre, dre_saldos_bancarios)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_saldo_bancario_por_ue_dre_falta_periodo(jwt_authenticated_client_sme, tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-ue-dre',
        'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_por_ue_dre_falta_conta(jwt_authenticated_client_sme, periodo_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-ue-dre',
        'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
