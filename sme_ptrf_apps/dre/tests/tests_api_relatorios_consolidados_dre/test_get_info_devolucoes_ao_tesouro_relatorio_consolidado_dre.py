import json
import pytest

from datetime import date

from model_bakery import baker

from rest_framework import status

pytestmark = pytest.mark.django_db

@pytest.fixture
def prestacao_conta(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        devolucao_tesouro=True,
        status='APROVADA',
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
def devolucao_ao_tesouro_1(prestacao_conta, tipo_devolucao_ao_tesouro, despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste 1'
    )

@pytest.fixture
def devolucao_ao_tesouro_2(prestacao_conta, tipo_devolucao_ao_tesouro, despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste 2'
    )

@pytest.fixture
def obs_devolucao_tesouro_relatorio_dre_consolidado(periodo, dre, tipo_conta, tipo_devolucao_ao_tesouro):
    return baker.make(
        'ObsDevolucaoRelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta,
        periodo=periodo,
        tipo_devolucao='TESOURO',
        tipo_devolucao_ao_tesouro=tipo_devolucao_ao_tesouro,
        observacao='Teste devolução ao tesouro'
    )

def test_api_get_info_devolucoes_ao_tesouro_relatorio(
    jwt_authenticated_client_relatorio_consolidado,
    dre,
    periodo,
    tipo_conta,
    prestacao_conta,
    tipo_devolucao_ao_tesouro,
    devolucao_ao_tesouro_1,
    devolucao_ao_tesouro_2,
    obs_devolucao_tesouro_relatorio_dre_consolidado
):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'tipo_nome': f'{tipo_devolucao_ao_tesouro.nome}',
            'tipo_uuid': f'{tipo_devolucao_ao_tesouro.uuid}',
            'ocorrencias': 2,
            'valor': 200.00,
            'observacao': 'Teste devolução ao tesouro',
        },
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_get_info_devolucoes_ao_tesouro_relatorio_sem_passa_dre(jwt_authenticated_client_relatorio_consolidado, dre, periodo, tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre',
        'operacao': 'info-devolucoes-ao-tesouro'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_devolucoes_ao_tesouro_relatorio_sem_passa_periodo(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                                      tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?dre={dre.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo',
        'operacao': 'info-devolucoes-ao-tesouro'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_devolucoes_ao_tesouro_relatorio_sem_passar_tipo_conta(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                                          tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?dre={dre.uuid}&periodo={periodo.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta',
        'operacao': 'info-devolucoes-ao-tesouro'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado
