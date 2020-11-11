import json
import pytest

from datetime import date
from model_bakery import baker

from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def conta_associacao_cheque(associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cheque,
    )


@pytest.fixture
def conta_associacao_cartao(associacao, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cartao,
    )


@pytest.fixture
def prestacao_conta(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        devolucao_tesouro=True,
        ressalvas_aprovacao='Texto ressalva',
        status='APROVADA',
    )


@pytest.fixture
def fechamento_conta_cartao(periodo, associacao, conta_associacao_cartao, acao_associacao, prestacao_conta):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        status='FECHADO',
        prestacao_conta=prestacao_conta,
    )


@pytest.fixture
def fechamento_conta_cheque_anterior(periodo_anterior, associacao, conta_associacao_cheque, acao_associacao,
                                     prestacao_conta_anterior):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=1000,
        total_despesas_capital=500,
        total_receitas_custeio=1000,
        total_repasses_custeio=1000,
        total_despesas_custeio=500,
        total_receitas_livre=1000,
        total_repasses_livre=1000,
        status='FECHADO',
        prestacao_conta=prestacao_conta_anterior,
    )


@pytest.fixture
def fechamento_conta_cheque(periodo, associacao, conta_associacao_cheque, acao_associacao, prestacao_conta,
                            fechamento_conta_cheque_anterior):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_conta_cheque_anterior,
        total_receitas_capital=1050,
        total_repasses_capital=1000,
        total_despesas_capital=500,
        total_receitas_custeio=1200,
        total_repasses_custeio=1000,
        total_receitas_devolucao_custeio=100,
        total_despesas_custeio=500,
        total_receitas_livre=1000,
        total_repasses_livre=1000,
        status='FECHADO',
        prestacao_conta=prestacao_conta,
    )


@pytest.fixture
def despesa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2019, 9, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2019, 9, 10),
        valor_total=100.00,
    )


@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


@pytest.fixture
def devolucao_ao_tesouro(prestacao_conta, tipo_devolucao_ao_tesouro, despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste'
    )

@pytest.fixture
def tipo_receita_rendimento():
    return baker.make('TipoReceita', nome='Rendimento', e_rendimento=True)

@pytest.fixture
def receita_rendimento(associacao, conta_associacao_cheque, acao_associacao, tipo_receita_rendimento):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=date(2019, 9, 10),
        valor=100.00,
        detalhe_outros="Rendimento",
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_rendimento,
        update_conferido=True,
        conferido=True,
        categoria_receita='CUSTEIO'
    )


@pytest.fixture
def previsao_repasse_sme_conta_cheque(periodo, associacao, conta_associacao_cheque):
    return baker.make(
        'PrevisaoRepasseSme',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao_cheque,
        valor_custeio=1000,
        valor_capital=2000,
        valor_livre=3000,
    )


@pytest.fixture
def previsao_repasse_sme_conta_cartao(periodo, associacao, conta_associacao_cartao):
    return baker.make(
        'PrevisaoRepasseSme',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        valor_custeio=1,
        valor_capital=1,
        valor_livre=1,
    )


def test_api_get_info_execucao_financeira_relatorio(
    jwt_authenticated_client,
    dre,
    periodo,
    tipo_conta_cheque,
    prestacao_conta,
    fechamento_conta_cartao,
    fechamento_conta_cheque,
    fechamento_conta_cheque_anterior,
    devolucao_ao_tesouro,
    receita_rendimento,
    conta_associacao_cheque,
    acao_associacao,
    previsao_repasse_sme_conta_cartao,
    previsao_repasse_sme_conta_cheque,
):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-execucao-financeira/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta_cheque.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'saldo_reprogramado_periodo_anterior_custeio': 500,
        'saldo_reprogramado_periodo_anterior_capital': 500,
        'saldo_reprogramado_periodo_anterior_livre': 1000,
        'saldo_reprogramado_periodo_anterior_total': 2000,

        'repasses_previstos_sme_custeio': 1000,
        'repasses_previstos_sme_capital': 2000,
        'repasses_previstos_sme_livre': 3000,
        'repasses_previstos_sme_total': 6000,

        'repasses_no_periodo_custeio': 1000,
        'repasses_no_periodo_capital': 1000,
        'repasses_no_periodo_livre': 1000,
        'repasses_no_periodo_total': 3000,

        'receitas_rendimento_no_periodo_custeio': 100,
        'receitas_rendimento_no_periodo_capital': 0,
        'receitas_rendimento_no_periodo_livre': 0,
        'receitas_rendimento_no_periodo_total': 100,

        'receitas_devolucao_no_periodo_custeio': 100,
        'receitas_devolucao_no_periodo_capital': 0,
        'receitas_devolucao_no_periodo_livre': 0,
        'receitas_devolucao_no_periodo_total': 100,

        'demais_creditos_no_periodo_custeio': 0,
        'demais_creditos_no_periodo_capital': 50,
        'demais_creditos_no_periodo_livre': 0,
        'demais_creditos_no_periodo_total': 50,

        'receitas_totais_no_periodo_custeio': 1200,
        'receitas_totais_no_periodo_capital': 1050,
        'receitas_totais_no_periodo_livre': 1000,
        'receitas_totais_no_periodo_total': 3250,

        'despesas_no_periodo_custeio': 500,
        'despesas_no_periodo_capital': 500,
        'despesas_no_periodo_total': 1000,

        'saldo_reprogramado_proximo_periodo_custeio': 1200,
        'saldo_reprogramado_proximo_periodo_capital': 1050,
        'saldo_reprogramado_proximo_periodo_livre': 2000,
        'saldo_reprogramado_proximo_periodo_total': 4250,

        'devolucoes_ao_tesouro_no_periodo_total': 100,
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
