import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_saldo_bancario_por_tipo_de_unidade(jwt_authenticated_client_sme, observacao_conciliacao_saldos_bancarios,
                                            periodo_saldos_bancarios,
                                            tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-tipo-unidade/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = [
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


def test_saldo_bancario_por_dre(jwt_authenticated_client_sme, observacao_conciliacao_saldos_bancarios,
                                periodo_saldos_bancarios,
                                tipo_conta_saldos_bancarios,
                                dre,
                                dre_saldos_bancarios,
                                ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = [
        {'nome_dre': dre_saldos_bancarios.nome, 'qtde_dre_informadas': 1, 'saldo_bancario_informado': 1000.0,
         'total_unidades': 1},
        {'nome_dre': dre.nome, 'qtde_dre_informadas': 0, 'saldo_bancario_informado': 0, 'total_unidades': 1},
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_saldo_bancario_por_dre_falta_periodo(jwt_authenticated_client_sme, tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-dre',
        'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_por_dre_falta_conta(jwt_authenticated_client_sme, periodo_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-dre',
        'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_por_ue_dre(jwt_authenticated_client_sme, observacao_conciliacao_saldos_bancarios,
                                   periodo_saldos_bancarios,
                                   tipo_conta_saldos_bancarios,
                                   dre,
                                   dre_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = [{'associacoes': [{'associacao': 'IFSP', 'saldo_total': 0},
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
                           'sigla_dre': dre_saldos_bancarios.sigla,
                           'uuid_dre': f'{dre_saldos_bancarios.uuid}'}]

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


def test_saldo_bancario_detalhes_associacoes(jwt_authenticated_client_sme,
                                             associacao_saldos_bancarios,
                                             observacao_conciliacao_saldos_bancarios,
                                             periodo_saldos_bancarios,
                                             tipo_conta_saldos_bancarios,
                                             dre,
                                             dre_saldos_bancarios,
                                             ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}&dre={dre_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = [
        {
            'nome': associacao_saldos_bancarios.nome,
            'obs_periodo__comprovante_extrato': '',
            'unidade__codigo_eol': associacao_saldos_bancarios.unidade.codigo_eol,
            'obs_periodo__saldo_extrato': 1000.0,
            'obs_periodo__uuid': f'{observacao_conciliacao_saldos_bancarios.uuid}',
            'obs_periodo__data_extrato': None
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_saldo_bancario_detalhes_associacoes_falta_periodo(jwt_authenticated_client_sme,
                                                           associacao_saldos_bancarios,
                                                           observacao_conciliacao_saldos_bancarios,
                                                           periodo_saldos_bancarios,
                                                           tipo_conta_saldos_bancarios,
                                                           dre,
                                                           dre_saldos_bancarios,
                                                           ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?conta={tipo_conta_saldos_bancarios.uuid}&dre={dre_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldos-detalhes-associacoes',
        'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_detalhes_associacoes_falta_conta(jwt_authenticated_client_sme,
                                                         associacao_saldos_bancarios,
                                                         observacao_conciliacao_saldos_bancarios,
                                                         periodo_saldos_bancarios,
                                                         tipo_conta_saldos_bancarios,
                                                         dre,
                                                         dre_saldos_bancarios,
                                                         ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&dre={dre_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldos-detalhes-associacoes',
        'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_detalhes_associacoes_falta_dre(jwt_authenticated_client_sme,
                                                       associacao_saldos_bancarios,
                                                       observacao_conciliacao_saldos_bancarios,
                                                       periodo_saldos_bancarios,
                                                       tipo_conta_saldos_bancarios,
                                                       dre,
                                                       dre_saldos_bancarios,
                                                       ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldos-detalhes-associacoes',
        'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_detalhes_associacoes_filtro_unidade(jwt_authenticated_client_sme,
                                                            associacao_saldos_bancarios,
                                                            observacao_conciliacao_saldos_bancarios,
                                                            periodo_saldos_bancarios,
                                                            tipo_conta_saldos_bancarios,
                                                            dre,
                                                            dre_saldos_bancarios,
                                                            ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}&dre={dre_saldos_bancarios.uuid}&unidade=Escola Teste',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = [
        {
            'nome': associacao_saldos_bancarios.nome,
            'obs_periodo__comprovante_extrato': '',
            'unidade__codigo_eol': associacao_saldos_bancarios.unidade.codigo_eol,
            'obs_periodo__saldo_extrato': 1000.0,
            'obs_periodo__uuid': f'{observacao_conciliacao_saldos_bancarios.uuid}',
            'obs_periodo__data_extrato': None
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_saldo_bancario_detalhes_associacoes_filtro_codigo_eol(jwt_authenticated_client_sme,
                                                               associacao_saldos_bancarios,
                                                               observacao_conciliacao_saldos_bancarios,
                                                               periodo_saldos_bancarios,
                                                               tipo_conta_saldos_bancarios,
                                                               dre,
                                                               dre_saldos_bancarios,
                                                               ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}&dre={dre_saldos_bancarios.uuid}&unidade=123457',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = [
        {
            'nome': associacao_saldos_bancarios.nome,
            'obs_periodo__comprovante_extrato': '',
            'unidade__codigo_eol': associacao_saldos_bancarios.unidade.codigo_eol,
            'obs_periodo__saldo_extrato': 1000.0,
            'obs_periodo__uuid': f'{observacao_conciliacao_saldos_bancarios.uuid}',
            'obs_periodo__data_extrato': None
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_saldo_bancario_detalhes_associacoes_filtro_tipo_unidade(jwt_authenticated_client_sme,
                                                                 associacao_saldos_bancarios,
                                                                 observacao_conciliacao_saldos_bancarios,
                                                                 periodo_saldos_bancarios,
                                                                 tipo_conta_saldos_bancarios,
                                                                 dre,
                                                                 dre_saldos_bancarios,
                                                                 ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}&dre={dre_saldos_bancarios.uuid}&tipo_ue=CEU',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = [
        {
            'nome': associacao_saldos_bancarios.nome,
            'obs_periodo__comprovante_extrato': '',
            'unidade__codigo_eol': associacao_saldos_bancarios.unidade.codigo_eol,
            'obs_periodo__saldo_extrato': 1000.0,
            'obs_periodo__uuid': f'{observacao_conciliacao_saldos_bancarios.uuid}',
            'obs_periodo__data_extrato': None
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
