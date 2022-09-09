import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_conta():
    return baker.make(
        'TipoConta',
        nome='Cheque',
        banco_nome='Banco do Inter',
        agencia='67945',
        numero_conta='935556-x',
        numero_cartao='987644164221'
    )


@pytest.fixture
def conta_associacao(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def prestacao_conta(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status='APROVADA',
    )


@pytest.fixture
def tipo_receita_devolucao(tipo_conta):
    return baker.make('TipoReceita', nome='Devolução', e_devolucao=True, aceita_capital=True, aceita_custeio=True,
                      tipos_conta=[tipo_conta])


@pytest.fixture
def detalhe_tipo_receita(tipo_receita_devolucao):
    return baker.make('DetalheTipoReceita', nome='Teste 1', tipo_receita=tipo_receita_devolucao)


@pytest.fixture
def receita_devolucao_1(associacao, conta_associacao, acao_associacao, tipo_receita_devolucao, prestacao_conta_iniciada,
                        detalhe_tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=date(2019, 9, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_devolucao,
        update_conferido=True,
        conferido=True,
        categoria_receita='CUSTEIO',
        detalhe_tipo_receita=detalhe_tipo_receita,
    )


@pytest.fixture
def receita_devolucao_2(associacao, conta_associacao, acao_associacao, tipo_receita_devolucao, prestacao_conta_iniciada,
                        detalhe_tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=date(2019, 9, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_devolucao,
        update_conferido=True,
        conferido=True,
        categoria_receita='CUSTEIO',
        detalhe_tipo_receita=detalhe_tipo_receita,
    )


@pytest.fixture
def obs_devolucao_conta_relatorio_dre_consolidado(periodo, dre, tipo_conta, detalhe_tipo_receita):
    return baker.make(
        'ObsDevolucaoRelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta,
        periodo=periodo,
        tipo_devolucao='CONTA',
        tipo_devolucao_a_conta=detalhe_tipo_receita,
        observacao='Teste devolução à conta'
    )

def test_api_get_info_devolucoes_conta_relatorio(
    jwt_authenticated_client_relatorio_consolidado,
    dre,
    periodo,
    tipo_conta,
    prestacao_conta,
    receita_devolucao_1,
    receita_devolucao_2,
    obs_devolucao_conta_relatorio_dre_consolidado
):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-conta/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'tipo_nome': 'Teste 1',
            'tipo_uuid': f'{receita_devolucao_1.detalhe_tipo_receita.uuid}',
            'ocorrencias': 2,
            'valor': 200.00,
            'observacao': 'Teste devolução à conta'
        },
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_get_info_devolucoes_conta_relatorio_sem_passa_dre(jwt_authenticated_client_relatorio_consolidado, dre, periodo, tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-conta/?periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre',
        'operacao': 'info-devolucoes-conta'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_devolucoes_conta_relatorio_sem_passa_periodo(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                                   tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-conta/?dre={dre.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo',
        'operacao': 'info-devolucoes-conta'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_devolucoes_conta_relatorio_sem_passar_tipo_conta(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                                       tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-conta/?dre={dre.uuid}&periodo={periodo.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta',
        'operacao': 'info-devolucoes-conta'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado
