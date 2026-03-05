from datetime import date
import json

import pytest

from rest_framework import status
from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao
from sme_ptrf_apps.core.models.unidade import Unidade

pytestmark = pytest.mark.django_db

associacoes_dict = {
    'IFSP': 0,
    'CMCT': 0,
    'CECI': 0,
    'CEI': 0,
    'CEMEI': 0,
    'CIEJA': 0,
    'EMEBS': 0,
    'EMEF': 0,
    'EMEFM': 0,
    'EMEI': 0,
    'CEU': 1000.0,
    'CEU CEI': 0,
    'CEU EMEF': 0,
    'CEU EMEI': 0,
    'CEU CEMEI': 0,
    'CEI DIRET': 0
}


def test_saldo_bancario_por_ue_dre(jwt_authenticated_client_sme, periodo_factory, associacao_factory, conta_associacao_factory, observacao_conciliacao_factory, unidade_factory):

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

    unidade = unidade_factory.create(tipo_unidade="CEU")

    associacao = associacao_factory.create(periodo_inicial=periodo_anterior_saldos_bancarios, unidade=unidade)

    conta_associacao = conta_associacao_factory.create(associacao=associacao, data_inicio=date(2019, 3, 20))

    observacao = observacao_conciliacao_factory.create(
        data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao, conta_associacao=conta_associacao)

    tipo_conta_saldos_bancarios = observacao.conta_associacao.tipo_conta

    dre_saldos_bancarios = observacao.associacao.unidade.dre

    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    dre_encontrada = next((obj for obj in result if obj["nome_dre"] == dre_saldos_bancarios.nome.replace(
        "DIRETORIA REGIONAL DE EDUCACAO", "").strip()), None)

    assert response.status_code == status.HTTP_200_OK
    for associacao_data in dre_encontrada['associacoes']:
        associacao = associacao_data['associacao']
        assert associacao_data['saldo_total'] == associacoes_dict.get(
            associacao, None), f"saldo_total for {associacao} is not {associacoes_dict.get(associacao, None)}"


def test_saldo_bancario_por_ue_dre_com_conta_nao_iniciada(jwt_authenticated_client_sme, periodo_factory, associacao_factory, conta_associacao_factory, observacao_conciliacao_factory, unidade_factory):
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

    unidade = unidade_factory.create(tipo_unidade="CEU")

    associacao = associacao_factory.create(periodo_inicial=periodo_anterior_saldos_bancarios, unidade=unidade)

    conta_associacao = conta_associacao_factory.create(associacao=associacao, data_inicio=None)

    observacao = observacao_conciliacao_factory.create(
        data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao, conta_associacao=conta_associacao)

    tipo_conta_saldos_bancarios = observacao.conta_associacao.tipo_conta

    dre_saldos_bancarios = observacao.associacao.unidade.dre

    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    dre_encontrada = next((obj for obj in result if obj["nome_dre"] == dre_saldos_bancarios.nome.replace(
        "DIRETORIA REGIONAL DE EDUCACAO", "").strip()), None)

    assert response.status_code == status.HTTP_200_OK
    for associacao_data in dre_encontrada['associacoes']:
        associacao = associacao_data['associacao']
        assert associacao_data['saldo_total'] == associacoes_dict.get(
            associacao, None), f"saldo_total for {associacao} is not {associacoes_dict.get(associacao, None)}"


def test_saldo_bancario_por_ue_dre_com_conta_encerrada(jwt_authenticated_client_sme, periodo_factory, associacao_factory, conta_associacao_factory, observacao_conciliacao_factory, unidade_factory, solicitacao_encerramento_conta_associacao_factory):
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

    unidade = unidade_factory.create(tipo_unidade="CEU")

    associacao = associacao_factory.create(periodo_inicial=periodo_anterior_saldos_bancarios, unidade=unidade)

    conta_associacao_encerrada = conta_associacao_factory.create(associacao=associacao, data_inicio=date(2019, 2, 20))

    solicitacao_encerramento_conta_associacao = solicitacao_encerramento_conta_associacao_factory.create(
        conta_associacao=conta_associacao_encerrada, status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA, data_de_encerramento_na_agencia=date(2019, 5, 1))

    observacao = observacao_conciliacao_factory.create(
        data_extrato=None, saldo_extrato=1000, periodo=periodo_saldos_bancarios, associacao=associacao, conta_associacao=conta_associacao_encerrada)

    tipo_conta_saldos_bancarios = observacao.conta_associacao.tipo_conta

    dre_saldos_bancarios = observacao.associacao.unidade.dre

    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-ue-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    dre_encontrada = next((obj for obj in result if obj["nome_dre"] == dre_saldos_bancarios.nome.replace(
        "DIRETORIA REGIONAL DE EDUCACAO", "").strip()), None)

    assert response.status_code == status.HTTP_200_OK
    for associacao_data in dre_encontrada['associacoes']:
        associacao = associacao_data['associacao']
        assert associacao_data['saldo_total'] == associacoes_dict.get(
            associacao, None), f"saldo_total for {associacao} is not {associacoes_dict.get(associacao, None)}"


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
