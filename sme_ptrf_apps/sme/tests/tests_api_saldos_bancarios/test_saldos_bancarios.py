from datetime import date
import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db
    
def test_saldo_bancario_detalhes_associacoes(jwt_authenticated_client_sme, periodo_factory, associacao_factory, observacao_conciliacao_factory):
    
    periodo_anterior_saldos_bancarios = periodo_factory.create(
        referencia="2019.1",
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 3, 31),
    )
    periodo_saldos_bancarios = periodo_factory.create(
        referencia="2019.2",
        data_inicio_realizacao_despesas=date(2019, 4, 1),
        data_fim_realizacao_despesas=date(2019, 8, 20),
        periodo_anterior=periodo_anterior_saldos_bancarios
    )
    
    associacao = associacao_factory.create(periodo_inicial=periodo_anterior_saldos_bancarios)
    
    observacao = observacao_conciliacao_factory.create(data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao)
    
    tipo_conta = observacao.conta_associacao.tipo_conta
    
    dre_saldos_bancarios = observacao.associacao.unidade.dre

    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta.uuid}&dre={dre_saldos_bancarios.uuid}',
        content_type='application/json')
    
    result = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    assert result[0]["nome"] == associacao.nome
    assert result[0]["obs_periodo__comprovante_extrato"] == ''
    assert result[0]["unidade__codigo_eol"] == associacao.unidade.codigo_eol
    assert result[0]["unidade__nome"] == associacao.unidade.nome
    assert result[0]["obs_periodo__saldo_extrato"] == 1000.0
    assert result[0]["obs_periodo__uuid"] == f'{observacao.uuid}'
    assert result[0]["obs_periodo__data_extrato"] == None

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


def test_saldo_bancario_detalhes_associacoes_filtro_unidade(jwt_authenticated_client_sme, periodo_factory, associacao_factory, observacao_conciliacao_factory):
    
    periodo_anterior_saldos_bancarios = periodo_factory.create(
        referencia="2019.1",
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 3, 31),
    )
    periodo_saldos_bancarios = periodo_factory.create(
        referencia="2019.2",
        data_inicio_realizacao_despesas=date(2019, 4, 1),
        data_fim_realizacao_despesas=date(2019, 8, 20),
        periodo_anterior=periodo_anterior_saldos_bancarios
    )
    
    associacao = associacao_factory.create(periodo_inicial=periodo_anterior_saldos_bancarios)
    
    observacao = observacao_conciliacao_factory.create(data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao)
    
    tipo_conta = observacao.conta_associacao.tipo_conta
    
    dre_saldos_bancarios = observacao.associacao.unidade.dre
    
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta.uuid}&dre={dre_saldos_bancarios.uuid}&unidade={associacao.nome}',
        content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result[0]["nome"] == associacao.nome
    assert result[0]["obs_periodo__comprovante_extrato"] == ''
    assert result[0]["unidade__codigo_eol"] == associacao.unidade.codigo_eol
    assert result[0]["unidade__nome"] == associacao.unidade.nome
    assert result[0]["obs_periodo__saldo_extrato"] == 1000.0
    assert result[0]["obs_periodo__uuid"] == f'{observacao.uuid}'
    assert result[0]["obs_periodo__data_extrato"] == None


def test_saldo_bancario_detalhes_associacoes_filtro_codigo_eol(jwt_authenticated_client_sme, periodo_factory, associacao_factory, observacao_conciliacao_factory):
    
    periodo_anterior_saldos_bancarios = periodo_factory.create(
        referencia="2019.1",
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 3, 31),
    )
    periodo_saldos_bancarios = periodo_factory.create(
        referencia="2019.2",
        data_inicio_realizacao_despesas=date(2019, 4, 1),
        data_fim_realizacao_despesas=date(2019, 8, 20),
        periodo_anterior=periodo_anterior_saldos_bancarios
    )
    
    associacao = associacao_factory.create(periodo_inicial=periodo_anterior_saldos_bancarios)
    
    observacao = observacao_conciliacao_factory.create(data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao)
    
    tipo_conta = observacao.conta_associacao.tipo_conta
    
    dre_saldos_bancarios = observacao.associacao.unidade.dre
    
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta.uuid}&dre={dre_saldos_bancarios.uuid}&unidade={associacao}',
        content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result[0]["nome"] == associacao.nome
    assert result[0]["obs_periodo__comprovante_extrato"] == ''
    assert result[0]["unidade__codigo_eol"] == associacao.unidade.codigo_eol
    assert result[0]["unidade__nome"] == associacao.unidade.nome
    assert result[0]["obs_periodo__saldo_extrato"] == 1000.0
    assert result[0]["obs_periodo__uuid"] == f'{observacao.uuid}'
    assert result[0]["obs_periodo__data_extrato"] == None


def test_saldo_bancario_detalhes_associacoes_filtro_tipo_unidade(jwt_authenticated_client_sme, periodo_factory, associacao_factory, observacao_conciliacao_factory):
    
    periodo_anterior_saldos_bancarios = periodo_factory.create(
        referencia="2019.1",
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 3, 31),
    )
    periodo_saldos_bancarios = periodo_factory.create(
        referencia="2019.2",
        data_inicio_realizacao_despesas=date(2019, 4, 1),
        data_fim_realizacao_despesas=date(2019, 8, 20),
        periodo_anterior=periodo_anterior_saldos_bancarios
    )
    
    associacao = associacao_factory.create(periodo_inicial=periodo_anterior_saldos_bancarios)
    
    observacao = observacao_conciliacao_factory.create(data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao)
    
    tipo_conta = observacao.conta_associacao.tipo_conta
    
    dre_saldos_bancarios = observacao.associacao.unidade.dre
    
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/saldos-detalhes-associacoes/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta.uuid}&dre={dre_saldos_bancarios.uuid}&tipo_ue={associacao.unidade.tipo_unidade}',
        content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result[0]["nome"] == associacao.nome
    assert result[0]["obs_periodo__comprovante_extrato"] == ''
    assert result[0]["unidade__codigo_eol"] == associacao.unidade.codigo_eol
    assert result[0]["unidade__nome"] == associacao.unidade.nome
    assert result[0]["obs_periodo__saldo_extrato"] == 1000.0
    assert result[0]["obs_periodo__uuid"] == f'{observacao.uuid}'
    assert result[0]["obs_periodo__data_extrato"] == None


def test_saldo_bancario_detalhes_associacoes_exporta_xlsx(jwt_authenticated_client_sme,
                                                         periodo_saldos_bancarios,
                                                         tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/exporta_xlsx_dres/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "mensagem": "Arquivo na fila para processamento."
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_saldo_bancario_detalhes_associacoes_falta_periodo_exporta_xlsx(jwt_authenticated_client_sme,
                                                                       tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/exporta_xlsx_dres/?conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldos-detalhes-associacoes',
        'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_detalhes_associacoes_falta_conta_exporta_xlsx(jwt_authenticated_client_sme,
                                                                     periodo_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme-detalhes/exporta_xlsx_dres/?periodo={periodo_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldos-detalhes-associacoes',
        'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST

