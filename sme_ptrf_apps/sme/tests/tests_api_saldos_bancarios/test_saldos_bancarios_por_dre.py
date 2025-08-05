from datetime import date
import json

import pytest

from rest_framework import status
from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao

pytestmark = pytest.mark.django_db


def test_saldo_bancario_por_dre(jwt_authenticated_client_sme, periodo_factory, associacao_factory, observacao_conciliacao_factory, conta_associacao_factory):

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

    conta_associacao = conta_associacao_factory.create(associacao=associacao, data_inicio=date(2019, 2, 20))

    observacao = observacao_conciliacao_factory.create(
        data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao, conta_associacao=conta_associacao)

    tipo_conta_saldos_bancarios = observacao.conta_associacao.tipo_conta

    dre_saldos_bancarios = observacao.associacao.unidade.dre

    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    assert result[0]["nome_dre"] == dre_saldos_bancarios.nome.replace("DIRETORIA REGIONAL DE EDUCACAO", "").strip()
    assert result[0]["qtde_dre_informadas"] == 1
    assert result[0]["saldo_bancario_informado"] == 1000.0
    assert result[0]["total_unidades"] == 1
    assert response.status_code == status.HTTP_200_OK


def test_saldo_bancario_por_dre_com_conta_nao_iniciada(jwt_authenticated_client_sme,
                                                       periodo_factory,
                                                       associacao_factory,
                                                       observacao_conciliacao_factory,
                                                       conta_associacao_factory
                                                       ):

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

    conta_associacao_nao_iniciada = conta_associacao_factory.create(associacao=associacao, data_inicio=None)

    observacao = observacao_conciliacao_factory.create(
        data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao, conta_associacao=conta_associacao_nao_iniciada)

    tipo_conta_saldos_bancarios = observacao.conta_associacao.tipo_conta

    dre_saldos_bancarios = observacao.associacao.unidade.dre

    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    assert result[0]["nome_dre"] == dre_saldos_bancarios.nome.replace("DIRETORIA REGIONAL DE EDUCACAO", "").strip()
    assert result[0]["qtde_dre_informadas"] == 1
    assert result[0]["saldo_bancario_informado"] == 1000.0
    assert result[0]["total_unidades"] == 1
    assert response.status_code == status.HTTP_200_OK


def test_saldo_bancario_por_dre_com_conta_encerrada(jwt_authenticated_client_sme,
                                                    periodo_factory,
                                                    associacao_factory,
                                                    observacao_conciliacao_factory,
                                                    conta_associacao_factory,
                                                    solicitacao_encerramento_conta_associacao_factory,
                                                    ):
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

    conta_associacao_encerrada = conta_associacao_factory.create(associacao=associacao, data_inicio=date(2019, 2, 20))

    solicitacao_encerramento_conta_associacao = solicitacao_encerramento_conta_associacao_factory.create(
        conta_associacao=conta_associacao_encerrada, status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA, data_de_encerramento_na_agencia=date(2019, 5, 1))

    observacao = observacao_conciliacao_factory.create(
        data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao, conta_associacao=conta_associacao_encerrada)

    tipo_conta_saldos_bancarios = observacao.conta_associacao.tipo_conta

    dre_saldos_bancarios = observacao.associacao.unidade.dre

    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    assert result[0]["nome_dre"] == dre_saldos_bancarios.nome.replace("DIRETORIA REGIONAL DE EDUCACAO", "").strip()
    assert result[0]["qtde_dre_informadas"] == 1
    assert result[0]["saldo_bancario_informado"] == 1000.0
    assert result[0]["total_unidades"] == 1
    assert response.status_code == status.HTTP_200_OK


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
